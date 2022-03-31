# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import docker
import os
import psutil
import socket
import subprocess
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Union
from .memgraph import Memgraph


MEMGRAPH_DEFAULT_BINARY_PATH = "/usr/lib/memgraph/memgraph"
MEMGRAPH_DEFAULT_PORT = 7687
LOOPBACK_ADDRESS = "127.0.0.1"
WILDCARD_ADDRESS = "0.0.0.0"

TIMEOUT_ERROR_MESSAGE = "Waited too long for the port {port} on host {host} to start accepting connections."
DOCKER_TIMEOUT_ETTOT_MESSAGE = "Waited too long for the Docker container to start."
MEMGRAPH_CONNECTION_ERROR_MESSAGE = "The Memgraph process probably died."


class DockerImage(Enum):
    MEMGRAPH = "memgraph/memgraph"
    MAGE = "memgraph/memgraph-mage"


class DockerContainerStatus(Enum):
    EXITED = "exited"
    PAUSED = "paused"
    RESTARTING = "restarting"
    RUNNING = "running"


def wait_for_port(
    host: str = LOOPBACK_ADDRESS, port: int = MEMGRAPH_DEFAULT_PORT, delay: float = 0.01, timeout: float = 5.0
) -> None:
    """Wait for a TCP port to become available.

    Args:
        host: A string representing the IP address that is being checked.
        port: A string representing the port that is being checked.
        delay: A float that defines how long to wait between retries.
        timeout: A float that defines how long to wait for the port.

    Raises:
      TimeoutError: Raises an error when the host and port are not accepting
        connections after the timeout period has passed.
    """
    start_time = time.perf_counter()
    time.sleep(delay)
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(delay)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(TIMEOUT_ERROR_MESSAGE.format(port=port, host=host)) from ex


def wait_for_docker_container(container: "docker.Container", delay: float = 0.01, timeout: float = 5.0) -> None:
    """Wait for a Docker container to enter the status `running`.

    Args:
        container: The Docker container to wait for.
        delay: A float that defines how long to wait between retries.
        timeout: A float that defines how long to wait for the status.

    Raises:
      TimeoutError: Raises an error when the container isn't running after the
        timeout period has passed.
    """
    start_time = time.perf_counter()
    time.sleep(delay)
    container.reload()
    while container.status != DockerContainerStatus.RUNNING.value:
        time.sleep(delay)
        if time.perf_counter() - start_time >= timeout:
            raise TimeoutError(DOCKER_TIMEOUT_ETTOT_MESSAGE)
        container.reload()


class MemgraphInstance(ABC):
    def __init__(
        self,
        host: str = WILDCARD_ADDRESS,
        port: int = MEMGRAPH_DEFAULT_PORT,
        config: Dict[str, Union[str, int, bool]] = dict(),
    ) -> None:
        self.host = host
        self.port = port
        self.config = config
        self.proc_mg = None
        self.config["--bolt-port"] = self.port
        self.config["--bolt-address"] = self.host

    def set_config(self, config: Dict[str, Union[str, int, bool]]) -> None:
        self.config.update(config)

    def connect(self) -> "Memgraph":
        self.memgraph = Memgraph(self.host, self.port)
        if not self.is_running():
            raise ConnectionError(MEMGRAPH_CONNECTION_ERROR_MESSAGE)
        return self.memgraph

    @abstractmethod
    def start(self, restart: bool = False) -> None:
        pass

    @abstractmethod
    def start_and_connect(self, restart: bool = False) -> "Memgraph":
        pass

    @abstractmethod
    def stop(self) -> Any:
        pass

    @abstractmethod
    def is_running(self) -> bool:
        pass


class MemgraphInstanceBinary(MemgraphInstance):
    """A class for managing Memgraph instances started from binary files on Unix
    systems.

    Attributes:
      binary_path: A string representing the path to a Memgraph binary
        file.
      user: A string representing the user that should start the Memgraph
        process.
    """

    def __init__(self, binary_path: str = MEMGRAPH_DEFAULT_BINARY_PATH, user: str = "", **data) -> None:
        super().__init__(**data)
        self.binary_path = binary_path
        self.user = user

    def start(self, restart: bool = False) -> None:
        """Start the Memgraph instance from a binary file.

        Attributes:
            restart: A bool indicating if the instance should be
              restarted if it's already running.
        """
        if not restart and self.is_running():
            return

        self.stop()
        args_mg = f"{self.binary_path } " + (" ").join([f"{k}={v}" for k, v in self.config.items()])
        if self.user != "":
            args_mg = f"sudo runuser -l {self.user} -c '{args_mg}'"

        self.proc_mg = subprocess.Popen(args_mg, shell=True)
        wait_for_port(self.host, self.port)

    def start_and_connect(self, restart: bool = False) -> "Memgraph":
        """Start the Memgraph instance from a binary file and return the
          connection object.

        Attributes:
            restart: A bool indicating if the instance should be
              restarted if it's already running.
        """
        self.start(restart=restart)
        return self.connect()

    def stop(self) -> None:
        """Stop the Memgraph instance."""
        if not self.is_running():
            return
        procs = set()
        process = psutil.Process(self.proc_mg.pid)
        procs.add(process)
        for proc in process.children(recursive=True):
            procs.add(proc)
            os.system(f"sudo kill {proc.pid}")
        process.kill()
        psutil.wait_procs(procs)

    def is_running(self) -> bool:
        """Check if the Memgraph instance is still running."""
        if self.proc_mg is None:
            return False
        if self.proc_mg.poll() is not None:
            return False
        return True


class MemgraphInstanceDocker(MemgraphInstance):
    """A class for managing Memgraph instances started in Docker containers.

    Attributes:
      docker_image: An enum representing the Docker image. Values:
        `DockerImage.MEMGRAPH` and `DockerImage.MAGE`.
      docker_image_tag: A string representing the tag of the Docker image.
    """

    def __init__(
        self, docker_image: DockerImage = DockerImage.MEMGRAPH, docker_image_tag: str = "latest", **data
    ) -> None:
        super().__init__(**data)
        self.docker_image = docker_image
        self.docker_image_tag = docker_image_tag
        self._client = docker.from_env()
        self._container = None

    def start(self, restart: bool = False) -> None:
        """Start the Memgraph instance in a Docker container.

        Attributes:
            restart: A bool indicating if the instance should be
              restarted if it's already running.
        """
        if not restart and self.is_running():
            return
        self.stop()
        self._container = self._client.containers.run(
            image=self.docker_image.value + ":" + self.docker_image_tag,
            command=MEMGRAPH_DEFAULT_BINARY_PATH + " " + (" ").join([f"{k}={v}" for k, v in self.config.items()]),
            detach=True,
            ports={f"{self.port}/tcp": self.port},
        )
        wait_for_docker_container(self._container, delay=1)

    def start_and_connect(self, restart: bool = False) -> "Memgraph":
        """Start the Memgraph instance in a Docker container and return the
          connection object.

        Attributes:
            restart: A bool indicating if the instance should be
              restarted if it's already running.
        """
        self.start(restart=restart)
        return self.connect()

    def stop(self) -> Dict:
        """Stop the Memgraph instance."""
        if not self.is_running():
            return
        self._container.stop()
        return self._container.wait()

    def is_running(self) -> bool:
        """Check if the Memgraph instance is still running."""
        if self._container is None:
            return False
        self._container.reload()
        if self._container.status == DockerContainerStatus.RUNNING.value:
            return True
        return False
