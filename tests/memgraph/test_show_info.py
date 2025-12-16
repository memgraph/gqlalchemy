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

from unittest.mock import patch

from gqlalchemy.vendors.memgraph import Memgraph


def test_get_storage_info():
    """Test get_storage_info returns storage information."""
    memgraph = Memgraph()
    mock_result = [
        {"storage info": "name", "value": "memgraph"},
        {"storage info": "vertex_count", "value": 100},
        {"storage info": "edge_count", "value": 200},
    ]

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter(mock_result)) as mock:
        result = memgraph.get_storage_info()

    mock.assert_called_with("SHOW STORAGE INFO;")
    assert result == mock_result


def test_get_build_info():
    """Test get_build_info returns build information."""
    memgraph = Memgraph()
    mock_result = [
        {"build info": "build_type", "value": "Release"},
    ]

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter(mock_result)) as mock:
        result = memgraph.get_build_info()

    mock.assert_called_with("SHOW BUILD INFO;")
    assert result == mock_result
