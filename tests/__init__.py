SAMPLE_CONFIGURATION = """
[tada-engine]
host = 127.0.0.1

frontend_port = 5601
backend_port = 5602
monitoring_port = 5603
admin_port = 5680

log_level = DEBUG
admin_log_file = /tmp/var/log/tada-engine-admin.log
engine_log_file = /tmp/var/log/tada-engine.log

proxy_pid_file = /tmp/var/run/tada-engine-proxy.pid
master_pid_file = /tmp/var/run/tada-engine-master.pid
minion_pid_file = /tmp/var/run/tada-engine-minion.pid

data_path = /tmp/var/lib/tada-engine/
minion_cache = /tmp/var/lib/tada-engine/minion
master_cache = /tmp/var/lib/tada-engine/master
"""


def add(taskrunner_class, row):
    try:
        a, b = row.split(',')
        a = int(a)
        b = int(b)
        result = a + b

    except (AttributeError, Exception):
        result = None

    finally:
        return result

