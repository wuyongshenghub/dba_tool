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
    parser.add_argument("-info",type=str,dest="info",choices=["sys","myall","mysql","mytop"],help="sys:print system info;myall:print system and mysql info;mysql:print mysql info;mytop:print mysql processlist info",default="sys")
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

def execute_remote_host_command(cmd):
    result = {}
    try:
        # print "\033[32m %s \033[0m" %cmd
        host_client = link_ssh_host()
        stdin,stdout,stderr = host_client.exec_command(cmd)
        result['error'] = stderr.readlines()
        result['output'] = stdout.readlines()
        if len(result['error'])>0:
            print "\033[31m result[error][0].replace('\n','') \033[0m"
        else:
            pass
    except:
        host_client.close()
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

# system_info()



if __name__=="__main__":
    args = chk_arguments()
    if not args.info or args.info == 'sys':
        system_info()
    elif args.info == 'mysql':
        print "print mysql....."

