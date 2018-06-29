SAMPLE_CONFIGURATION = """
[tada-engine]
host = 127.0.0.1
frontend_port = 5501
backend_port = 5601
monitoring_port = 5701

log_level = DEBUG
log_file = /var/log/tada-engine--test.log

proxy_pid_file = /var/run/tada-engine-proxy--test.pid
master_pid_file = /var/run/tada-engine-master--test.pid
minion_pid_file = /var/run/tada-engine-minion--test.pid
"""
