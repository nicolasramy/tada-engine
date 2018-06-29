# Tada Engine

A simple workers engine

## Development

### Dependencies

- setproctitle
- termcolor
- pyzmq
- uvloop

### Prepare environment

```bash
docker build -t tada-engine .
docker run --rm --name tada-engine-test -i -t -v $PWD:/app tada-engine sh
```

## Roadmap

- [ ] Configuration file 
- [ ] Implement uvloop in Minion
- [ ] Implement RAFT Protocol
- [ ] Merge Master & Proxy
- [ ] Create a simple solution to add external task
- [ ] Consolidate Daemon (specially for Proxy)
- [ ] Travis-CI
- [ ] Coveralls
- [ ] Pypi


## How to tests?

Documentation about testing:
- http://docs.python-guide.org/en/latest/writing/tests/


## Misc

- Use a job queue?
    - Beanstalk
    - Redis
    - In Memory?
- Internal compression for data exchange (snappy)
- use LevelDB
- use snappy
- use SQLite
- web interface
    - dashboard
    - monitoring
    - create / edit workflow
- workflow
    - linear
    - unordered
    - graph       
- input formats
    - JSONLines `.jsonl`
    - JSON `.json`     
    - CSV `.csv`     
    - TSV `.tsv`     
    - Text file `.txt`
- input / output sources    
    - file
    - http
    - stream
    - db
    - aws s3
    - HDFS, etc ...
    - ...
             

### Improvements     

- How to measure performance
- Migrate from ZMQ to AsyncIO TCP
- Raft Protocol // 1 type of process, master = minion with a special task for mastering

