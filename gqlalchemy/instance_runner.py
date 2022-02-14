# Copyright 2021 Memgraph Ltd.
#
# Use of this software is governed by the Business Source License
# included in the file licenses/BSL.txt; by using this file, you agree to be bound by the terms of the Business Source
# License, and you may not use this file except in compliance with the Business Source License.
#
# As of the Change Date specified in that file, in accordance with
# the Business Source License, use of this software will be governed
# by the Apache License, Version 2.0, included in the file
# licenses/APL.txt.

import docker
import os
import subprocess
import tempfile
import time
import socket
from abc import ABC, abstractmethod
from typing import Dict, Union, Optional
from .memgraph import Memgraph
import pwd
import grp
import os


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
MEMGRAPH_BINARY = os.path.join(BUILD_DIR, "memgraph")


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
        self, host: str = "127.0.0.1", port: int = 7687, username: str = "", password: str = "", encrypted=False
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.encrypted = encrypted
        self.config = {}
        self.proc_mg = None

    def set_config(self, config: Dict[str, Union[str, int, bool]]):
        self.config.update(config)

    def connect(self):
        self.memgraph = Memgraph(self.host, self.port, self.username, self.password, self.encrypted)
        assert self.is_running(), "The Memgraph process died!"
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
    def start(self, restart=False, binary_path="/usr/lib/memgraph/memgraph", user: str = ""):
        self.binary_path = binary_path
        if not restart and self.is_running():
            return
        self.stop()

        args_mg = f"{self.binary_path }" + (" ").join([f"{k} {v}" for k, v in self.config])
        args_mg += f" --bolt-address {self.host} --bolt-port {self.port}"
        args_mg = (f"sudo -u {user} " if user != "" else "") + args_mg

        # TODO: Process should be started as user memgraph
        self.proc_mg = subprocess.Popen(args_mg, shell=True)
        wait_for_port(self.host, self.port)

        self.connect()
        return self.memgraph

    def stop(self):
        if not self.is_running():
            return
        self.proc_mg.terminate()
        code = self.proc_mg.wait()
        print(f"Exit code: {code}")

    def is_running(self):
        if self.proc_mg is None:
            return False
        if self.proc_mg.poll() is not None:
            return False
        return True


class MemgraphInstanceDocker(MemgraphInstance):
    def __init__(self, **data):
        super().__init__(**data)
        self.client = docker.from_env()
        self.container = None

    def start(self, restart=False):
        if not restart and self.is_running():
            return
        self.stop()

        self.container = self.client.containers.run(
            "memgraph/memgraph-mage", detach=True, ports={f"7687/tcp": self.port}
        )
        wait_for_port(self.host, self.port)

        self.connect()
        return self.memgraph

    def stop(self):
        if not self.is_running():
            return
        code = self.container.stop()
        print(f"Exit code: {code}")

    def is_running(self):
        if self.container is None:
            return False
        for container in self.client.containers.list():
            if container.id == self.container.id:
                return True
        return False
