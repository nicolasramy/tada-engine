# Tada! Engine

A simple workers engine

## Development

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

