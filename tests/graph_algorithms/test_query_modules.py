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

from gqlalchemy.graph_algorithms.query_modules import QueryModule


def test_set_inputs_exception():
    """setting an argument that doesn't exist shouldn't be possible"""
    dummy_dict = {
        "is_editable": True,
        "is_write": False,
        "name": "dummy",
        "path": "",
        "signature": "dummy() :: ()",
        "arguments": [{}, {}],
        "returns": [{}, {}],
    }

    qm = QueryModule(**dummy_dict)
    with pytest.raises(KeyError):
        qm.set_argument_values(dummy=0)


def test_set_and_get_arguments():
    """use QueryModule class to set inputs and return in form for call()"""
    color_graph_yield = {
        "is_editable": True,
        "is_write": False,
        "name": "graph_coloring.color_graph",
        "path": "/home/user/mage/python/graph_coloring.py",
        "signature": 'graph_coloring.color_graph(parameters = {} :: MAP, edge_property = "weight" :: STRING) :: (color :: STRING, node :: STRING)',
        "arguments": [
            {"type": "MAP", "name": "parameters", "default": "{}"},
            {"type": "STRING", "name": "edge_property", "default": "weight"},
        ],
        "returns": [{"type": "STRING", "name": "color"}, {"type": "STRING", "name": "node"}],
    }

    qm = QueryModule(**color_graph_yield)
    qm.set_argument_values(edge_property="none")
    assert qm.get_arguments_for_call() == '{}, "none"'
