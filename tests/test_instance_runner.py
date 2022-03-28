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

import pytest
from gqlalchemy import MemgraphInstanceBinary, MemgraphInstanceDocker


def test_start_memgraph_docker():
    memgraph_instance = MemgraphInstanceDocker(port=7688)
    memgraph = memgraph_instance.start()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()


@pytest.mark.ubuntu
def test_start_memgraph_binary():
    memgraph_instance = MemgraphInstanceBinary(
        port=7689, config={"--data-directory": "data"}, binary_path="/usr/lib/memgraph/memgraph", user="memgraph"
    )
    memgraph = memgraph_instance.start()
    assert list(memgraph.execute_and_fetch("RETURN 100 AS result"))[0]["result"] == 100
    memgraph_instance.stop()
