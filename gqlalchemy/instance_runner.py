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


import socket
import subprocess
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Union

try:
    import docker
except ModuleNotFoundError:
    docker = None
import psutil

from gqlalchemy.exceptions import (
    GQLAlchemyWaitForConnectionError,
    GQLAlchemyWaitForDockerError,
    GQLAlchemyWaitForPortError,
    raise_if_not_imported,
)
from gqlalchemy.vendors.memgraph import Memgraph


MEMGRAPH_DEFAULT_BINARY_PATH = "/usr/lib/memgraph/memgraph"
MEMGRAPH_DEFAULT_PORT = 7687
MEMGRAPH_CONFIG_BOLT_PORT = "--bolt-port"
MEMGRAPH_CONFIG_BOLT_ADDRESS = "--bolt-address"
DOCKER_IMAGE_TAG_LATEST = "latest"
LOOPBACK_ADDRESS = "127.0.0.1"
WILDCARD_ADDRESS = "0.0.0.0"


class DockerImage(Enum):
    MEMGRAPH = "memgraph/memgraph"
    MAGE = "memgraph/memgraph-mage"


class DockerContainerStatus(Enum):
    EXITED = "exited"
    PAUSED = "paused"
    RESTARTING = "restarting"
    RUNNING = "running"


def wait_for_port(
    host: str = LOOPBACK_ADDRESS,
    port: int = MEMGRAPH_DEFAULT_PORT,
    delay: float = 0.01,
    timeout: float = 5.0,
    backoff: int = 2,
) -> None:
    """Wait for a TCP port to become available.

    Args:
        host: A string representing the IP address that is being checked.
        port: A string representing the port that is being checked.
        delay: A float that defines how long to wait between retries.
        timeout: A float that defines how long to wait for the port.
        backoff: An integer used for multiplying the delay.

    Raises:
      TimeoutError: Raises an error when the host and port are not accepting
        connections after the timeout period has passed.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(delay)
            if time.perf_counter() - start_time >= timeout:
                raise GQLAlchemyWaitForPortError(port=port, host=host) from ex

        delay *= backoff


def wait_for_docker_container(container, delay: float = 0.01, timeout: float = 5.0, backoff: int = 2) -> None:
    """Wait for a Docker container to enter the status `running`.

    Args:
        container: The Docker container to wait for.
        delay: A float that defines how long to wait between retries.
        timeout: A float that defines how long to wait for the status.
        backoff: An integer used for multiplying the delay.

    Raises:
      TimeoutError: Raises an error when the container isn't running after the
        timeout period has passed.
    """
    start_time = time.perf_counter()
    while container.status != DockerContainerStatus.RUNNING.value:
        container.reload()
        time.sleep(delay)

        if time.perf_counter() - start_time >= timeout:
            raise GQLAlchemyWaitForDockerError

        delay *= backoff


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
        self.config[MEMGRAPH_CONFIG_BOLT_PORT] = self.port
        self.config[MEMGRAPH_CONFIG_BOLT_ADDRESS] = self.host
        self._memgraph = None

    @property
    def memgraph(self) -> Memgraph:
        if self._memgraph is None:
            self._memgraph = Memgraph(self.host, self.port)

        return self._memgraph

    def set_config(self, config: Dict[str, Union[str, int, bool]]) -> None:
        self.config.update(config)

    def connect(self) -> "Memgraph":
        if not self.is_running():
            raise GQLAlchemyWaitForConnectionError

        return self.memgraph

    def start_and_connect(self, restart: bool = False) -> "Memgraph":
        """Start the Memgraph instance and return the
          connection object.

        Attributes:
            restart: A bool indicating if the instance should be
              restarted if it's already running.
        """
        self.start(restart=restart)

        return self.connect()

    def start(self, restart: bool = False) -> None:
        """Start the Memgraph instance.

        Attributes:
            restart: A bool indicating if the instance should be
              restarted if it's already running.
        """
        if not restart and self.is_running():
            return

        self.stop()
        self._start_instance()

    def stop(self) -> Any:
        """Stop the Memgraph instance."""
        if not self.is_running():
            return

        self._stop_instance()

    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def _start_instance(self) -> None:
        pass

    @abstractmethod
    def _stop_instance(self) -> Any:
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

    def _start_instance(self) -> None:
        args_mg = f"{self.binary_path } " + (" ").join([f"{k}={v}" for k, v in self.config.items()])
        if self.user != "":
            args_mg = f"runuser -l {self.user} -c '{args_mg}'"

        self.proc_mg = subprocess.Popen(args_mg, shell=True)
        wait_for_port(self.host, self.port)

    def _stop_instance(self) -> None:
        procs = set()
        process = psutil.Process(self.proc_mg.pid)
        procs.add(process)
        for proc in process.children(recursive=True):
            procs.add(proc)
            proc.kill()

        process.kill()
        psutil.wait_procs(procs)

    def is_running(self) -> bool:
        """Check if the Memgraph instance is still running."""
        return self.proc_mg is not None and self.proc_mg.poll() is None


class MemgraphInstanceDocker(MemgraphInstance):
    """A class for managing Memgraph instances started in Docker containers.

    Attributes:
      docker_image: An enum representing the Docker image. Values:
        `DockerImage.MEMGRAPH` and `DockerImage.MAGE`.
      docker_image_tag: A string representing the tag of the Docker image.
    """

    def __init__(
        self, docker_image: DockerImage = DockerImage.MEMGRAPH, docker_image_tag: str = DOCKER_IMAGE_TAG_LATEST, **data
    ) -> None:
        raise_if_not_imported(dependency=docker, dependency_name="docker")

        super().__init__(**data)
        self.docker_image = docker_image
        self.docker_image_tag = docker_image_tag
        self._client = docker.from_env()
        self._container = None

    def _start_instance(self) -> None:
        self._container = self._client.containers.run(
            image=f"{self.docker_image.value}:{self.docker_image_tag}",
            command=f"{MEMGRAPH_DEFAULT_BINARY_PATH} {(' ').join([f'{k}={v}' for k, v in self.config.items()])}",
            detach=True,
            ports={f"{self.port}/tcp": self.port},
        )
        wait_for_docker_container(self._container)

    def _stop_instance(self) -> Dict:
        self._container.stop()

        return self._container.wait()

    def is_running(self) -> bool:
        """Check if the Memgraph instance is still running."""
        if self._container is None:
            return False

        self._container.reload()

        return self._container.status == DockerContainerStatus.RUNNING.value
