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

- [ ] Implement uvloop in Minion
- [ ] Create a simple solution to add external task
- [ ] Consolidate Daemon (specially for Proxy)
- [ ] Travis-CI
- [ ] Coveralls
- [ ] Pypi


## How to tests?

Documentation about testing:
- http://docs.python-guide.org/en/latest/writing/tests/


