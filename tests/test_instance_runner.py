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

import os
import pathlib
import pytest

import docker

from gqlalchemy.instance_runner import (
    DockerImage,
    MemgraphInstanceBinary,
    MemgraphInstanceDocker,
    wait_for_port,
    wait_for_docker_container,
)


def test_wait_for_port():
    with pytest.raises(TimeoutError):
        wait_for_port(port=0000, timeout=1)


@pytest.mark.docker
def test_wait_for_docker_container():
    container = docker.from_env().containers.create(DockerImage.MEMGRAPH.value)
    with pytest.raises(TimeoutError):
        wait_for_docker_container(container, timeout=1)


@pytest.mark.docker
def test_start_and_connect_memgraph_docker():
    memgraph_instance = MemgraphInstanceDocker(port=7690)
    memgraph = memgraph_instance.start_and_connect()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    assert memgraph_instance.is_running()
    memgraph_instance.stop()
    assert not memgraph_instance.is_running()


@pytest.mark.docker
def test_start_and_connect_memgraph_docker_config():
    memgraph_instance = MemgraphInstanceDocker(port=7691, config={"--log-level": "TRACE"})
    memgraph = memgraph_instance.start_and_connect()
    assert memgraph_instance.is_running()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()
    assert not memgraph_instance.is_running()


@pytest.mark.docker
def test_start_memgraph_docker_connect():
    memgraph_instance = MemgraphInstanceDocker(port=7692)
    memgraph_instance.start()
    assert memgraph_instance.is_running()
    memgraph = memgraph_instance.connect()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()
    assert not memgraph_instance.is_running()


@pytest.mark.ubuntu
def test_start_and_connect_memgraph_binary():
    path = pathlib.Path().resolve() / "memgraph_one"
    os.system(f"mkdir {path}")
    os.system(f"sudo chown -R memgraph:memgraph {path}")
    memgraph_instance = MemgraphInstanceBinary(
        port=7693, config={"--data-directory": str(path)}, binary_path="/usr/lib/memgraph/memgraph", user="memgraph"
    )
    memgraph = memgraph_instance.start_and_connect()
    assert memgraph_instance.is_running()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()
    assert not memgraph_instance.is_running()
    os.system(f"rm -rf {path}")


@pytest.mark.ubuntu
def test_start_and_connect_memgraph_binary_config():
    path = pathlib.Path().resolve() / "memgraph_two/"
    os.system(f"mkdir {path}")
    os.system(f"sudo chown -R memgraph:memgraph {path}")
    memgraph_instance = MemgraphInstanceBinary(
        port=7694, config={"--data-directory": str(path)}, binary_path="/usr/lib/memgraph/memgraph", user="memgraph"
    )
    memgraph = memgraph_instance.start_and_connect()
    assert memgraph_instance.is_running()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()
    assert not memgraph_instance.is_running()
    os.system(f"rm -rf {path}")


@pytest.mark.ubuntu
def test_start_memgraph_binary_connect():
    path = pathlib.Path().resolve() / "memgraph_three"
    os.system(f"mkdir {path}")
    os.system(f"sudo chown -R memgraph:memgraph {path}")
    memgraph_instance = MemgraphInstanceBinary(
        port=7695, config={"--data-directory": str(path)}, binary_path="/usr/lib/memgraph/memgraph", user="memgraph"
    )
    memgraph_instance.start()
    assert memgraph_instance.is_running()
    memgraph = memgraph_instance.connect()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()
    assert not memgraph_instance.is_running()
    os.system(f"rm -rf {path}")
