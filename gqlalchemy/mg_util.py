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

import copy
import os
import subprocess
import sys
import tempfile
import time
from typing import Dict, Union
from .memgraph import Memgraph

import mgclient

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
MEMGRAPH_BINARY = os.path.join(BUILD_DIR, "memgraph")


def wait_for_server(port, delay=0.01):
    cmd = ["nc", "-z", "-w", "1", "127.0.0.1", str(port)]
    count = 0
    while subprocess.call(cmd) != 0:
        time.sleep(0.01)
        if count > 10 / 0.01:
            print("Could not wait for server on port", port, "to startup!")
            sys.exit(1)
        count += 1
    time.sleep(delay)


class MemgraphInstance:
    def __init__(self, host: str = "127.0.0.1", port: int = 7687) -> None:
        self.host = host
        self.port = port
        self.config = {}
        self.proc_mg = None

    def set_config(self, config: Dict[str, Union[str, int, bool]]):
        self.config.update(config)

    def query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def is_running(self):
        if self.proc_mg is None:
            return False
        if self.proc_mg.poll() is not None:
            return False
        return True

    def stop(self):
        if not self.is_running():
            return
        self.proc_mg.terminate()
        code = self.proc_mg.wait()
        assert code == 0, "The Memgraph process exited with non-zero!"

    def start_from_binary(self, binary_path, restart=False):
        self.binary_path = binary_path
        if not restart and self.is_running():
            return
        self.stop()
        self.data_directory = tempfile.TemporaryDirectory()
        args_mg = f"{self.binary_path} --data-directory {self.data_directory.name}" + (" ").join(
            [f"{k} {v}" for k, v in self.config]
        )
        self.proc_mg = subprocess.Popen(args_mg, shell=True)
        wait_for_server(self.port)

        self.db = Memgraph(host=self.host, port=self.port)
        assert self.is_running(), "The Memgraph process died!"
        return self.db

    def start_with_docker(self, restart=False):
        if not restart and self.is_running():
            return
        self.stop()
        self.data_directory = tempfile.TemporaryDirectory()
        args_mg = f"sudo docker run -p 7687:7687 memgraph/memgraph-mage " + (" ").join([f"{k} {v}" for k, v in self.config])
        self.proc_mg = subprocess.Popen(args_mg, shell=True)
        wait_for_server(self.port)

        self.db = Memgraph(host=self.host, port=self.port)
        assert self.is_running(), "The Memgraph process died!"
        return self.db
