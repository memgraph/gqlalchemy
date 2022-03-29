---
sidebar_label: instance_runner
title: gqlalchemy.instance_runner
---

#### wait\_for\_port

```python
def wait_for_port(host: str = "127.0.0.1", port: int = 7687, delay: float = 0.01, timeout: float = 5.0) -> None
```

Wait for a TCP port to become available.

**Arguments**:

- `host` _str_ - The IP address that is being checked.
- `port` _str_ - The port that is being checked.
- `delay` _float_ - A float that defines how long to wait between retries.
- `timeout` _float_ - A float that defines how long to wait for the port.
  

**Raises**:

- `TimeoutError` - Raises an error when the host and port are not accepting
  connections after the timeout period has passed.

#### wait\_for\_docker\_container

```python
def wait_for_docker_container(container: "docker.Container", delay: float = 0.01, timeout: float = 5.0) -> None
```

Wait for a Docker container to enter the status `running`.

**Arguments**:

- `container` _docker.Container_ - The Docker container to wait for.
- `delay` _float_ - A float that defines how long to wait between retries.
- `timeout` _float_ - A float that defines how long to wait for the status.
  

**Raises**:

- `TimeoutError` - Raises an error when the container isn&#x27;t running after the
  timeout period has passed.

## MemgraphInstanceBinary Objects

```python
class MemgraphInstanceBinary(MemgraphInstance)
```

A class for managing Memgraph instances started from binary files on Unix
systems.

**Attributes**:

- `binary_path` _str_ - A string representing the path to a Memgraph binary
  file.
- `user` _str_ - A string representing the user that should start the Memgraph
  process.

#### start

```python
def start(restart: bool = False) -> "Memgraph"
```

Start the Memgraph instance and return the connection object.

**Attributes**:

- `restart` _bool_ - A bool indicating if the instance should be
  restarted if it&#x27;s already running.

#### stop

```python
def stop() -> int
```

Stop the Memgraph instance.

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

- `docker_image` _DockerImage_ - An enum representing the Docker image. Values:
  `DockerImage.MEMGRAPH` and `DockerImage.MAGE`.
- `docker_image_tag` _str_ - A string representing the tag of the Docker image.

#### start

```python
def start(restart: bool = False) -> "Memgraph"
```

Start the Memgraph instance and return the connection object.

**Attributes**:

- `restart` _bool_ - A bool indicating if the instance should be
  restarted if it&#x27;s already running.

#### stop

```python
def stop() -> Dict
```

Stop the Memgraph instance.

#### is\_running

```python
def is_running() -> bool
```

Check if the Memgraph instance is still running.

