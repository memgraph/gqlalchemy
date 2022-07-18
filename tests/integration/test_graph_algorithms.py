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
import unittest.mock as mock
from typing import List

from gqlalchemy.graph_algorithms.query_modules import QueryModule, parse_query_module_signature
from gqlalchemy import Memgraph, QueryBuilder


@pytest.mark.parametrize(
    "signature, arguments, returns",
    [
        ("dummy_module.1(num :: NUMBER) :: ()", [{"name": "num", "type": "NUMBER"}], []),
        (
            "dummy_module.2(lst :: LIST OF STRING, num = 3 :: NUMBER) :: (ret :: STRING)",
            [{"name": "lst", "type": "LIST OF STRING"}, {"name": "num", "type": "NUMBER", "default": 3}],
            [{"name": "ret", "type": "STRING"}],
        ),
    ],
)
def test_parse_signature(signature: str, arguments: List, returns: List):
    """test functionality of parsing a module signature"""
    assert arguments, returns == parse_query_module_signature(signature=signature)


def test_get_procedures(memgraph: Memgraph):
    """test get procedures with mock execute_and_fetch method, so MAGE query
    modules are not needed for testing"""

    mock_modules = [
        {
            "is_editable": True,
            "is_write": False,
            "name": "max_flow.get_flow",
            "path": "/home/user/mage/python/max_flow.py",
            "signature": 'max_flow.get_flow(start_v :: NODE, end_v :: NODE, edge_property = "weight" :: STRING) :: (max_flow :: NUMBER)',
        },
        {
            "is_editable": True,
            "is_write": False,
            "name": "max_flow.get_paths",
            "path": "/home/user/mage/python/max_flow.py",
            "signature": 'max_flow.get_paths(start_v :: NODE, end_v :: NODE, edge_property = "weight" :: STRING) :: (flow :: NUMBER, path :: PATH)',
        },
    ]

    mock_execute_and_fetch = mock.Mock()
    mock_execute_and_fetch.return_value = mock_modules

    real_execute_and_fetch = memgraph.execute_and_fetch

    def mock_execute_and_fetch_wrapper(query):
        if query == "CALL mg.procedures() YIELD *;":
            return mock_execute_and_fetch(query)
        else:
            return real_execute_and_fetch(query)

    memgraph.execute_and_fetch = mock_execute_and_fetch_wrapper

    assert str(memgraph.get_procedures()[0]) == "max_flow.get_flow"


def test_query_module_with_query_builder():
    mock_module = {
        "is_editable": True,
        "is_write": False,
        "name": "max_flow.get_flow",
        "path": "/home/user/mage/python/max_flow.py",
        "signature": 'max_flow.get_flow(start_v :: NODE, end_v :: NODE, edge_property = "weight" :: STRING) :: (max_flow :: NUMBER)',
    }

    query_module = QueryModule(**mock_module)

    query_module.set_argument_values(start_v=None, end_v=None)

    query_builder = QueryBuilder().call(procedure=query_module, arguments=query_module.get_arguments_for_call())
    expected_query = ' CALL max_flow.get_flow(None, None, "weight") '

    with mock.patch.object(Memgraph, "execute", return_value=None) as m:
        query_builder.execute()

    m.assert_called_with(expected_query)
