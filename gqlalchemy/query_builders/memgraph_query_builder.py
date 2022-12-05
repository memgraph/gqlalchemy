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

from typing import Optional, Union, Tuple, Iterable

from gqlalchemy.query_builders.declarative_base import (  # noqa F401
    Call,
    Create,
    DeclarativeBase,
    DeclarativeBaseTypes,
    Foreach,
    Match,
    Merge,
    Operator,
    Order,
    PartialQuery,
    Return,
    Unwind,
    With,
)
from gqlalchemy.vendors.database_client import DatabaseClient
from gqlalchemy.vendors.memgraph import Memgraph
from gqlalchemy.utilities import CypherVariable


class MemgraphQueryBuilderTypes(DeclarativeBaseTypes):
    LOAD_CSV = "LOAD_CSV"


class LoadCsvPartialQuery(PartialQuery):
    def __init__(self, path: str, header: bool, row: str):
        super().__init__(DeclarativeBaseTypes.LOAD_CSV)
        self.path = path
        self.header = header
        self.row = row

    def construct_query(self) -> str:
        return f" LOAD CSV FROM '{self.path}' " + ("WITH" if self.header else "NO") + f" HEADER AS {self.row} "


class QueryBuilder(DeclarativeBase):
    def __init__(self, connection: Optional[Memgraph] = None):
        super().__init__(connection)

    def load_csv(self, path: str, header: bool, row: str) -> "DeclarativeBase":
        """Load data from a CSV file by executing a Cypher query for each row.

        Args:
            path: A string representing the path to the CSV file.
            header: A bool indicating if the CSV file starts with a header row.
            row: A string representing the name of the variable for iterating
              over each row.

        Returns:
            A `DeclarativeBase` instance for constructing queries.

        Examples:
            Load CSV with header:

            Python: `load_csv(path="path/to/my/file.csv", header=True, row="row").return_().execute()`
            Cypher: `LOAD CSV FROM 'path/to/my/file.csv' WITH HEADER AS row RETURN *;`

            Load CSV without header:

            Python: `load_csv(path='path/to/my/file.csv', header=False, row='row').return_().execute()`
            Cypher: `LOAD CSV FROM 'path/to/my/file.csv' NO HEADER AS row RETURN *;`
        """
        self._query.append(LoadCsvPartialQuery(path, header, row))

        return self

    def construct_subgraph_query(
        self, node_label: Optional[str] = None, relationship_types: Optional[Union[str, Iterable[str]]] = None
    ) -> str:
        """Constructs a MATCH query defining a subgraph using zero or one node labels and relationship types.

        Args:
            node_label (Optional[str], optional): node label to be used in subgraph
            relationship_types (Optional[Union[str, Iterable[str]]], optional): types of relationships used in subgraph.

        Returns:
            str: a MATCH query for a path with given node labels and relationship types
        """
        query = " MATCH p="
        if node_label is None:
            node = "()"
        else:
            node = f"(:{node_label.upper()})"

        query += node + "-"

        if isinstance(relationship_types, str):
            query += f"[:{relationship_types}]"
        elif isinstance(relationship_types, Iterable):
            rels = " | :".join(relationship_types)
            query += f"[:{rels}]"

        # directed is OK only if we have single label, homogenous graphs
        query += "->" + node

        return query

    def call(
        self,
        procedure: str,
        arguments: Optional[Union[str, Tuple[Union[str, int, float]]]] = None,
        node_label: Optional[str] = None,
        relationship_types: Optional[Union[str, Iterable[str]]] = None,
        subgraph_query: str = None,
    ) -> "DeclarativeBase":
        """Override of base class method to support Memgraph's subgraph functionality.

        Method can be called with node labels and relationship types, both being optional, which are used to construct
        a subgraph, or if neither is provided, a subgraph query is used, which can be passed as a string representing a
        Cypher query defining the MATCH clause which selects the nodes and relationships to use.

        Args:
            procedure: A string representing the name of the procedure in the
              format `query_module.procedure`.
            arguments: A string representing the arguments of the procedure in
              text format.
            node_label: Label of nodes to be used in the subgraph.
            relationship_types: Types of relationships to be used in the subgraph.
            subgraph_query: Optional way to define the subgraph via a Cypher MATCH clause.

        Returns:
            A `DeclarativeBase` instance for constructing queries.

        Examples:
            Python: `call('export_util.json', '/home/user', "LABEL", ["TYPE1", "TYPE2"]).execute()
            Cypher: `MATCH p=(:LABEL)-[:TYPE1 | :TYPE2]->(:LABEL) WITH project(p) AS graph
                    CALL export_util.json(graph, '/home/user')`

            or

            Python: `call('export_util.json', '/home/user', subgraph_query="MATCH (:LABEL)-[:TYPE]->(:LABEL)").execute()
            Cypher: `MATCH p=(:LABEL)-[:TYPE1]->(:LABEL) WITH project(p) AS graph
                    CALL export_util.json(graph, '/home/user')`
        """

        if not (node_label is None and relationship_types is None):
            subgraph_query = self.construct_subgraph_query(node_label=node_label, relationship_types=relationship_types)

        if subgraph_query is not None:
            self._query.append(ProjectPartialQuery(subgraph_query=subgraph_query))

            if isinstance(arguments, str):
                arguments = (CypherVariable(name="graph"), arguments)
            elif isinstance(arguments, tuple):
                arguments = (CypherVariable(name="graph"), *arguments)
            else:
                arguments = CypherVariable(name="graph")

        super().call(procedure=procedure, arguments=arguments)

        return self


class LoadCsv(DeclarativeBase):
    def __init__(self, path: str, header: bool, row: str, connection: Optional[DatabaseClient] = None):
        super().__init__(connection)
        self._query.append(LoadCsvPartialQuery(path, header, row))


class ProjectPartialQuery(PartialQuery):
    def __init__(self, subgraph_query):
        super().__init__(DeclarativeBaseTypes.MATCH)
        self.query = subgraph_query

    def construct_query(self) -> str:
        """Constructs a Project partial querty. Given a Match query, adds path identifier if needed
        And appends the WITH clause."""
        query = self.query
        location = query.index("(")
        if query[location - 1] != "=":
            query = query[:location] + "p=" + query[location:]
        return f" {query} WITH project(p) AS graph "
