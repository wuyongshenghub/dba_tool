# dba_tool
For the database and daily inspection system系统及数据库日常巡检

### 使用
    1.
    系统信息
	python dba_tool.py
	DBA tools
	Hostname        |vm2
	Uptime          |17:10:19 up 1 day
	IP Addr         |127.0.0.1
	IP Addr         |192.168.137.11
	Memory          |989 MB
	Platform        |CentOS release 6.2 (Final)
	CPU Cores       |1
	CPU ModelName   |Intel(R) Core(TM) i3-4150 CPU @ 3.50GHz
	FS:/boot        |428M of free 485M
	FS:/work        |8.2G of free 20G
	FS:/            |3.2G of free 18G

	2.
	MySQL QPS/TPS/ins/upd/del
	thread:run/connect/create/cache
	slow:slow_sql/tmp table/disk tmp table
	bytes: Bytes_received/Bytes_sent
	python dba_tool.py -info mysql
	DBA tools:192.168.137.11
	---------+-------mysql-status-------+-----threads-----+-----slow-----+----bytes-------
	time     |   QPS  TPS  ins  upd  del| run  con cre cac| sql  tmp Dtmp|   recv   send
	---------+--------------------------+-----------------+--------------+----------------
	17:03:09 |    6    0    0    0    0 |  3   14  32  18 |  0    3   0  |  3.347K   1.838K
	17:03:11 |    9    0    0    0    0 |  3   14  32  18 |  0    3   0  |  2.64K    1.555K
	17:03:14 |    6    0    0    0    0 |  3   14  32  18 |  0    3   0  |  2.292K   1.416K
	17:03:16 |    6    0    0    0    0 |  3   14  32  18 |  0    3   0  |  3.336K   1.833K
	17:03:19 |    9    0    0    0    0 |  3   14  32  18 |  0    3   0  |  2.391K   1.421K
	17:03:21 |    6    0    0    0    0 |  3   14  32  18 |  0    3   0  |  3.336K   1.833K
	17:03:24 |    6    0    0    0    0 |  3   14  32  18 |  0    3   0  |  1.248K   999B


