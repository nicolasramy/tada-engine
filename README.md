# Tada! Engine

A simple workers engine

## Development

[![Travis CI](https://travis-ci.org/nicolasramy/tada-engine.svg?branch=master)](https://travis-ci.org/nicolasramy/tada-engine)
[![Coveralls](https://coveralls.io/repos/github/nicolasramy/tada-engine/badge.svg?branch=master)](https://coveralls.io/github/nicolasramy/tada-engine?branch=master)
[![Coveralls](https://coveralls.io/repos/github/nicolasramy/tada-engine/badge.svg?branch=develop)](https://coveralls.io/github/nicolasramy/tada-engine?branch=develop)

### Dependencies

- plyvel
- setproctitle
- termcolor
- pyzmq
- uvloop
- ujson

### Prepare environment

```bash
docker build -t tada-engine .
docker run --rm --name tada-engine-test -i -t -v $PWD:/app tada-engine sh
```

```bash
docker exec -it tada-engine-test sh
```


## How to tests?

Documentation about testing:
- http://docs.python-guide.org/en/latest/writing/tests/

