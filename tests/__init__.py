SAMPLE_CONFIGURATION = """
[tada-engine]
host = 127.0.0.1

frontend_port = 5601
backend_port = 5602
monitoring_port = 5603
http_port =  5680

log_level = DEBUG
log_file = /tmp/var/log/tada-engine--test.log

proxy_pid_file = /tmp/var/run/tada-engine-proxy--test.pid
master_pid_file = /tmp/var/run/tada-engine-master--test.pid
minion_pid_file = /tmp/var/run/tada-engine-minion--test.pid

data_path = /tmp/var/lib/tada-engine/
minion_cache = /tmp/var/lib/tada-engine/minion
master_cache = /tmp/var/lib/tada-engine/master
"""
