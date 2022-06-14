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

from gqlalchemy import Memgraph
from gqlalchemy.exceptions import GQLAlchemyFileNotFoundError


@pytest.mark.parametrize(
    "file_path, module_name, module_remove_name",
    [
        ("gqlalchemy/query_modules/push_streams/kafka.py", "kafka.py", "kafka.py"),
    ],
)
def test_add_query_module_valid(file_path, module_name, remove_module_memgraph):
    memgraph = remove_module_memgraph.add_query_module(file_path=file_path, module_name=module_name)

    module_paths = list(memgraph.execute_and_fetch("CALL mg.get_module_files() YIELD path"))

    assert any("kafka" in path["path"] for path in module_paths)


@pytest.mark.parametrize(
    "file_path, module_name",
    [
        ("path_doesnt_exists", "fake"),
    ],
)
def test_add_query_module_invalid(file_path, module_name):
    with pytest.raises(GQLAlchemyFileNotFoundError):
        Memgraph().add_query_module(file_path=file_path, module_name=module_name)
