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
import subprocess
import time
import signal
import socket
from abc import ABC, abstractmethod
from typing import Dict, Union, Optional
from .memgraph import Memgraph
from enum import Enum


class DockerImage(Enum):
    MEMGRAPH = "memgraph/memgraph"
    MAGE = "memgraph/memgraph-mage"


def wait_for_port(host: str = "127.0.0.1", port: int = 7687, delay: float = 0.01, timeout: float = 5.0):
    start_time = time.perf_counter()
    time.sleep(2)
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(delay)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(
                    f"Waited too long for the port {port} on host {host} to start accepting connections."
                ) from ex


class MemgraphInstance(ABC):
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7687,
        config: Dict[str, Union[str, int, bool]] = dict(),
    ) -> None:
        self.host = host
        self.port = port
        self.config = config
        self.proc_mg = None
        print(self.config)
        print(type(self.config))
        self.config["--bolt-port"] = self.port

    def set_config(self, config: Dict[str, Union[str, int, bool]]):
        self.config.update(config)

    def connect(self):
        self.memgraph = Memgraph(self.host, self.port)
        if not self.is_running():
            raise ConnectionError("The Memgraph process probably died.")
        return self.memgraph

    @abstractmethod
    def is_running(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start(self, restart: bool = False, binary_path: Optional[str] = ""):
        pass


class MemgraphInstanceBinary(MemgraphInstance):
    def __init__(self, binary_path="/usr/lib/memgraph/memgraph", user="", **data):
        super().__init__(**data)
        self.binary_path = binary_path
        self.user = user

    def start(self, restart=False):
        if not restart and self.is_running():
            return
        self.stop()

        args_mg = f"{self.binary_path } " + (" ").join([f"{k}={repr(v)}" for k, v in self.config.items()])
        if self.user != "":
            args_mg = f"sudo runuser -l {self.user} -c '{args_mg}'"
        print(args_mg)
        self.proc_mg = subprocess.Popen(args_mg, shell=True, preexec_fn=os.setsid)
        wait_for_port(self.host, self.port)

        self.connect()
        return self.memgraph

    def stop(self):
        if not self.is_running():
            return
        os.killpg(os.getpgid(self.proc_mg.pid), signal.SIGTERM)
        self.proc_mg.wait()

    def is_running(self):
        if self.proc_mg is None:
            return False
        if self.proc_mg.poll() is not None:
            return False
        return True


class MemgraphInstanceDocker(MemgraphInstance):
    def __init__(self, docker_image: DockerImage = DockerImage.MEMGRAPH, docker_tag: str = "latest", **data):
        super().__init__(**data)
        self.docker_image = docker_image
        self.docker_tag = docker_tag
        self.client = docker.from_env()
        self.container = None

    def start(self, restart=False):
        if not restart and self.is_running():
            return
        self.stop()

        self.container = self.client.containers.run(
            image=self.docker_image.value + ":" + self.docker_tag,
            command="/usr/lib/memgraph/memgraph" + (" ").join([f"{k} {v}" for k, v in self.config.items()]),
            detach=True,
            ports={f"7687/tcp": self.port},
        )
        wait_for_port(self.host, self.port)

        self.connect()
        return self.memgraph

    def stop(self):
        if not self.is_running():
            return
        self.container.stop()

    def is_running(self):
        if self.container is None:
            return False
        for container in self.client.containers.list():
            if container.id == self.container.id:
                return True
        return False
