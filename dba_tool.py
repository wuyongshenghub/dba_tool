#encoding:utf-8

import paramiko
import argparse
from config import dba
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')

def chk_arguments():
    parser = argparse.ArgumentParser(description="input need to argument")
    parser.add_argument("-sh",type=str,dest="shost",help="connect ssh host")
    parser.add_argument("-sP",type=int,dest="sport",help="connect ssh port.(default 22)")
    parser.add_argument("-su",type=str,dest="suser",help="connect ssh user.(default root)")
    parser.add_argument("-sp",type=str,dest="spwd",help="connect ssh password")
    parser.add_argument("-mu",type=str,dest="muser",help="connect mysql user")
    parser.add_argument("-mp",type=str,dest="mpwd",help="connect mysql password")
    parser.add_argument("-mP",type=int,dest="mport",help="connect mysql port (default 3306)",default=3306)
    parser.add_argument("-i",type=int,dest="duration",help="refresh interval in secondes.(default 1ns)",default=1)
    parser.add_argument("-info",type=str,dest="info",choices=["sys","myall","mysql","mytop","innodb"],help="sys:print system info;myall:print system and mysql info;mysql:print mysql info;mytop:print mysql processlist info",default="sys")
    args = parser.parse_args()
    
    # 命令行中没有输入参数 从配置文件中读取
    if not args.shost:
        args.shost = dba.get('Shost')
    if not args.sport:
        args.sport = dba.get('Sport')
    if not args.suser:
        args.suser = dba.get('Suser')
    if not args.spwd:
        args.spwd = dba.get('Spwd')
    if not args.muser:
        args.muser = dba.get('Muser')
    if not args.mpwd:
        args.mpwd = dba.get('Mpwd')
    if not args.mport:
        args.mport = dba.get('Mport')
    return args

def link_ssh_host():
    args = chk_arguments()
    # 创建ssh
    host_client = paramiko.SSHClient()
    host_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host_client.connect(args.shost,int(args.sport),args.suser,args.spwd)
    return host_client

def get_disk_partition():
    # 挂载分区
    fs = {}
    # host_client = link_ssh_host()
    cmd_shell = "df -lh|egrep -v 'Filesystem|mapper|tmpfs'"
    # stdin,stdout,stderr = host_client.exec_command(cmd_shell)
    result = execute_remote_host_command(cmd_shell)
    # print result['output']
    for line in result['output']:
        line_fs = line[11:]
        fsx = line_fs.split()
        # fs[4],fs[0],fs[2]
        # fs[挂载点] = (总容量,可用容量)
        fs[fsx[4]] = (fsx[0],fsx[2])
    # for k,v in fs.items():
    return fs

def get_host_name():
    # 获取服务器名称
    cmd_shell = "hostname"
    result = execute_remote_host_command(cmd_shell)
    return result['output'][0]

def get_up_time():
    # 运行时长
    cmd_shell = "uptime|awk -F ',' '{print $1}'"
    result = execute_remote_host_command(cmd_shell)
    return result['output'][0].lstrip()

def get_ip_addr():
    #获取主机ip addr
    cmd_shell = "/sbin/ifconfig |grep 'inet'|grep -v 'inet6'|awk '{print $2}'|awk -F ':' '{print $2}'"
    result = execute_remote_host_command(cmd_shell)
    return result['output']

def get_host_mem():
    # 主机total内存
    cmd_shell = "free -m|grep 'Mem'|awk '{print $2}'"
    result = execute_remote_host_command(cmd_shell)
    return str(result['output'][0].split()[0])+' MB'

def get_host_platform():
    # 主机版本
    cmd_shell = "cat /etc/redhat-release"
    result = execute_remote_host_command(cmd_shell)
    return result['output'][0]

def get_host_core():
    # 主机cpu cores
    cmd_shell = "cat /proc/cpuinfo |grep processor|wc -l"
    result = execute_remote_host_command(cmd_shell)
    return result['output'][0]

def get_host_modal():
    # 主机 modal Name
    cmd_shell = "cat /proc/cpuinfo |grep 'model name'|awk -F ': ' '{print $2}'"
    result = execute_remote_host_command(cmd_shell)
    return result['output'][0].strip()

def get_mysql_status_per_sec():
    # QPS/TPS/ins/upd/del
    args = chk_arguments()
    res1={}
    res2={}
    thd = {}
    slow1 = {}
    slow2 = {}
    byte1 = {}
    byte2 = {}
    gap_time = 1
    # mysql status
    cmd="var=$(ps -ef|grep mysqld_safe|grep -v grep |head -1|awk '{print $9}'|sed s'/\/mysqld_safe//g');" \
        "export PATH=$var:$PATH ;" \
        " mysql -h " + args.shost + " -P " + str(args.mport) + " -u'" + args.muser + "' -p'"+ args.mpwd + "' -e " \
        "\"show global status where variable_name in('com_select','com_insert','com_delete','com_update');\""
    # print cmd
    #  mysql threads
    cmd_t = "var=$(ps -ef|grep mysqld_safe|grep -v grep |head -1|awk '{print $9}'|sed s'/\/mysqld_safe//g');" \
          "export PATH=$var:$PATH ;" \
          " mysql -h " + args.shost + " -P " + str(args.mport) + " -u'" + args.muser + "' -p'" + args.mpwd + "' -e " \
          "\"show global status where variable_name in('Threads_cached','Threads_connected','Threads_created','Threads_running');\""
    # mysql slow sql
    cmd_slow = "var=$(ps -ef|grep mysqld_safe|grep -v grep |head -1|awk '{print $9}'|sed s'/\/mysqld_safe//g');" \
               "export PATH=$var:$PATH ;" \
               " mysql -h " + args.shost + " -P " + str(args.mport) + " -u'" + args.muser + "' -p'" + args.mpwd + "' -e " \
               "\"show global status where variable_name in('Slow_queries','Created_tmp_tables','Created_tmp_disk_tables');\""
    # mysql bytes
    cmd_bytes = "var=$(ps -ef|grep mysqld_safe|grep -v grep |head -1|awk '{print $9}'|sed s'/\/mysqld_safe//g');" \
               "export PATH=$var:$PATH ;" \
               " mysql -h " + args.shost + " -P " + str(args.mport) + " -u'" + args.muser + "' -p'" + args.mpwd + "' -e " \
               "\"show global status where variable_name in('Bytes_received','Bytes_sent');\""

    while True:
        ret = execute_remote_host_command(cmd)
        for x in ret['output'][1:]:
            tmp = x.strip().split()
            res1[tmp[0]] = tmp[1]
        # slow tmp
        sret = execute_remote_host_command(cmd_slow)
        for s in sret['output'][1:]:
            rtmp = s.strip().split()
            slow1[rtmp[0]] = rtmp[1]
        # bytes
        bres = execute_remote_host_command(cmd_bytes)
        for b in bres['output'][1:]:
            btmp = b.strip().split()
            byte1[btmp[0]] = btmp[1]
        time.sleep(gap_time)
        ret = execute_remote_host_command(cmd)
        for x in ret['output'][1:]:
            sec_tmp = x.strip().split()
            res2[sec_tmp[0]] = sec_tmp[1]
        # slow tmp
        sret = execute_remote_host_command(cmd_slow)
        for s in sret['output'][1:]:
            stmp = s.strip().split()
            slow2[stmp[0]] = stmp[1]
        # bytes
        bres = execute_remote_host_command(cmd_bytes)
        for b in bres['output'][1:]:
            bbtmp = b.strip().split()
            byte2[bbtmp[0]] = bbtmp[1]

        qps = (int(res2['Com_select']) - int(res1['Com_select']))/gap_time
        ins = (int(res2['Com_insert']) - int(res1['Com_insert']))/gap_time
        upd = (int(res2['Com_update']) - int(res1['Com_update']))/gap_time
        delt = (int(res2['Com_delete']) - int(res1['Com_delete']))/gap_time
        tps = ins + upd + delt
        # slow tmp
        sql = int(slow2['Slow_queries']) - int(slow1['Slow_queries'])
        stmp = int(slow2['Created_tmp_tables']) - int(slow1['Created_tmp_tables'])
        Dtmp = int(slow2['Created_tmp_disk_tables']) - int(slow1['Created_tmp_disk_tables'])
        #byte
        send = (int(byte2['Bytes_sent']) - int(byte1['Bytes_sent']))
        recv = (int(byte2['Bytes_received']) - int(byte1['Bytes_received']))
        # thread
        ret = execute_remote_host_command(cmd_t)

        for t in ret['output'][1:]:
            tmp = t.strip().split()
            thd[tmp[0]] = tmp[1]
        if send <= 1000:
            send = str(send) + 'B'
        elif send > 1000 and send <=10000:
            send = str(send*1.0/1000) + 'K'
        elif send >10000 and send <=1000000:
            send = str(send*1.0/1000*1000) + 'M'
        else:
            send = str(send*1.0/1000*1000*1000) + 'G'
        if recv <= 1000:
            recv = str(recv) + 'B'
        elif recv > 1000 and recv <= 10000:
            recv = str(recv*1.0 / 1000) + 'K'
        elif recv > 10000 and recv <= 1000000:
            recv = str(recv*1.0 / 1000 * 1000) + 'M'
        else:
            recv = str(recv*1.0/1000*1000*1000) + 'G'
        dt = time.strftime("%H:%M:%S",time.localtime(time.time()))
        return (dt,qps,tps,ins,upd,delt,thd['Threads_running'],thd['Threads_connected'],thd['Threads_created'],thd['Threads_cached'],sql,stmp,Dtmp,send,recv)

def execute_remote_host_command(cmd):
    # global host_client
    result = {}
    # try:
    # print "\033[32m %s \033[0m" %cmd
    host_client = link_ssh_host()
    stdin,stdout,stderr = host_client.exec_command(cmd)
    # result['error'] = stderr.readlines()
    result['output'] = stdout.readlines()
        # if len(result['error'])>0:
        #     print "\033[31m result[error][0].replace('\n','') \033[0m"
        # else:
        #     pass
    # except:
    #     host_client.close()
    return result

def system_info():
    # 打印主机系统信息
    print "DBA tools \n" \
          "Hostname        |{0}"\
          "Uptime          |{1}"\
          "IP Addr         |{2}"\
          "IP Addr         |{3}"\
          "Memory          |{4}"\
          "\nPlatform        |{5}" \
          "CPU Cores       |{6}"\
          "CPU ModelName   |{7}".format(get_host_name(),get_up_time(),get_ip_addr()[1].lstrip(),get_ip_addr()[0].lstrip(),
                                   get_host_mem(),get_host_platform(),get_host_core(),get_host_modal())
    for k,v in get_disk_partition().items():
        # print  "FS:%-2s%7s%s of free %s"%(k.ljust(7,' '),'|',v[1],v[0])
        print  "FS:%s%s%s of free %s"%(k.ljust(13,' '),'|',v[1],v[0])

def get_mysql_status():
    print "DBA tools:%s"%get_ip_addr()[0].lstrip()
    usage = """
---------+-------mysql-status-------+-----threads-----+-----slow-----+----bytes-------
time     |   QPS  TPS  ins  upd  del| run  con cre cac| sql  tmp Dtmp|   recv   send
---------+--------------------------+-----------------+--------------+----------------"""
    print usage
    cnt = 0
    while True:
        cnt  = cnt + 1
        res = get_mysql_status_per_sec()
        if cnt == 10:
            cnt = 0
            print usage
        print "%s |    %s    %s    %s    %s    %s |  %s   %s  %s  %s |  %s    %s   %s  |  %s  %s" \
              %(res[0],res[1],res[2],
                res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13].ljust(7,' '),res[14].ljust(1,' '))



if __name__=="__main__":
    try:
        args = chk_arguments()
        if not args.info or args.info == 'sys':
            system_info()
        elif args.info == 'mysql':
            get_mysql_status()
        elif args.info == 'innodb':
            print "print innodb..."
    except KeyboardInterrupt:
        print 'thanks for using...'
        sys.exit(1)