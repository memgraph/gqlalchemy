---
sidebar_label: instance_runner
title: gqlalchemy.instance_runner
---

#### wait\_for\_port

```python
def wait_for_port(host: str = LOOPBACK_ADDRESS,
                  port: int = MEMGRAPH_DEFAULT_PORT,
                  delay: float = 0.01,
                  timeout: float = 5.0,
                  backoff: int = 2) -> None
```

Wait for a TCP port to become available.

**Arguments**:

- `host` - A string representing the IP address that is being checked.
- `port` - A string representing the port that is being checked.
- `delay` - A float that defines how long to wait between retries.
- `timeout` - A float that defines how long to wait for the port.
- `backoff` - An integer used for multiplying the delay.
  

**Raises**:

- `TimeoutError` - Raises an error when the host and port are not accepting
  connections after the timeout period has passed.

#### wait\_for\_docker\_container

```python
def wait_for_docker_container(container,
                              delay: float = 0.01,
                              timeout: float = 5.0,
                              backoff: int = 2) -> None
```

Wait for a Docker container to enter the status `running`.

**Arguments**:

- `container` - The Docker container to wait for.
- `delay` - A float that defines how long to wait between retries.
- `timeout` - A float that defines how long to wait for the status.
- `backoff` - An integer used for multiplying the delay.
  

**Raises**:

- `TimeoutError` - Raises an error when the container isn&#x27;t running after the
  timeout period has passed.

## MemgraphInstance Objects

```python
class MemgraphInstance(ABC)
```

#### start\_and\_connect

```python
def start_and_connect(restart: bool = False) -> "Memgraph"
```

Start the Memgraph instance and return the
connection object.

**Attributes**:

- `restart` - A bool indicating if the instance should be
  restarted if it&#x27;s already running.

#### start

```python
def start(restart: bool = False) -> None
```

Start the Memgraph instance.

**Attributes**:

- `restart` - A bool indicating if the instance should be
  restarted if it&#x27;s already running.

#### stop

```python
def stop() -> Any
```

Stop the Memgraph instance.

## MemgraphInstanceBinary Objects

```python
class MemgraphInstanceBinary(MemgraphInstance)
```

A class for managing Memgraph instances started from binary files on Unix
systems.

**Attributes**:

- `binary_path` - A string representing the path to a Memgraph binary
  file.
- `user` - A string representing the user that should start the Memgraph
  process.

#### is\_running

```python
def is_running() -> bool
```

Check if the Memgraph instance is still running.

## MemgraphInstanceDocker Objects

```python
class MemgraphInstanceDocker(MemgraphInstance)
```

A class for managing Memgraph instances started in Docker containers.

**Attributes**:

- `docker_image` - An enum representing the Docker image. Values:
  `DockerImage.MEMGRAPH` and `DockerImage.MAGE`.
- `docker_image_tag` - A string representing the tag of the Docker image.

#### is\_running

```python
def is_running() -> bool
```

Check if the Memgraph instance is still running.

