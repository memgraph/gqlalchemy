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

from gqlalchemy import Memgraph
from gqlalchemy.graph_algorithms.query_builder import MemgraphQueryBuilder
from gqlalchemy.query_builders.memgraph_query_builder import QueryBuilder

import pytest


@pytest.mark.skip(reason="we are not keeping signatures up to date.")
def test_memgraph_query_builder_methods_exist(memgraph: Memgraph):
    """
    Tests functionality if all the procedures that are defined
    in the Memgraph extended query builder are present in the code.
    """

    mg_qb = MemgraphQueryBuilder()
    simple_qb = QueryBuilder()

    mg_qb_methods = set([method_name for method_name in dir(mg_qb) if callable(getattr(mg_qb, method_name))])

    simple_qb_methods = set(
        [method_name for method_name in dir(simple_qb) if callable(getattr(simple_qb, method_name))]
    )

    query_module_names = mg_qb_methods - simple_qb_methods
    actual_query_module_names = [procedure.name.replace(".", "_", 1) for procedure in memgraph.get_procedures()]

    print(f"Query module names: {query_module_names}\n\n")
    print(f"Actual: {actual_query_module_names}")

    for qm_name in query_module_names:
        assert qm_name in actual_query_module_names

    for qm_name in actual_query_module_names:
        assert qm_name in query_module_names
