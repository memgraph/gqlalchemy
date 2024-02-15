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

from typing import Optional, Union, Tuple, List
from string import ascii_lowercase

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
from gqlalchemy.utilities import CypherVariable, CypherNode, CypherRelationship, RelationshipDirection


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

    def _construct_subgraph_path(
        self,
        relationship_types: Optional[Union[str, List[List[str]]]] = None,
        relationship_directions: Optional[
            Union[RelationshipDirection, List[RelationshipDirection]]
        ] = RelationshipDirection.RIGHT,
    ) -> str:
        """Constructs a MATCH query defining a subgraph using node labels and relationship types.

        Args:
            relationship_types: A string or list of lists of types of relationships used in the subgraph.
            relationship_directions: Enums representing directions.

        Returns:
            a string representing a MATCH query for a path with given node labels and relationship types.
        """

        query = f"{CypherNode(variable=ascii_lowercase[0])}"
        for i in range(len(relationship_types)):
            query += f"{CypherRelationship(relationship_types[i], relationship_directions[i])}{CypherNode()}"

        return query

    def call(
        self,
        procedure: str,
        arguments: Optional[Union[str, Tuple[Union[str, int, float]]]] = None,
        node_labels: Optional[Union[str, List[List[str]]]] = None,
        relationship_types: Optional[Union[str, List[List[str]]]] = None,
        relationship_directions: Optional[
            Union[RelationshipDirection, List[RelationshipDirection]]
        ] = RelationshipDirection.RIGHT,
        subgraph_path: str = None,
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
            node_labels: Either a string, which is then used as the label for all nodes, or
                         a list of lists defining all labels for every node
            relationship_types: Types of relationships to be used in the subgraph. Either a
                                single type or a list of lists defining all types for every relationship
            relationship_directions: Directions of the relationships.
            subgraph_path: Optional way to define the subgraph via a Cypher MATCH clause.

        Returns:
            A `DeclarativeBase` instance for constructing queries.

        Examples:
            Python: `call('export_util.json', '/home/user', "LABEL", ["TYPE1", "TYPE2"]).execute()
            Cypher: `MATCH p=(a)-[:TYPE1 | :TYPE2]->(b) WHERE (a:LABEL) AND (b:LABEL)
                     WITH project(p) AS graph CALL export_util.json(graph, '/home/user')`

            or

            Python: `call('export_util.json', '/home/user', subgraph_path="(:LABEL)-[:TYPE]->(:LABEL)").execute()
            Cypher: `MATCH p=(:LABEL)-[:TYPE1]->(:LABEL) WITH project(p) AS graph
                    CALL export_util.json(graph, '/home/user')`
        """

        if not (node_labels is None and relationship_types is None):
            if isinstance(relationship_types, str):
                relationship_types = [[relationship_types]] * (
                    len(node_labels) - 1 if isinstance(node_labels, list) else 1
                )

            if isinstance(node_labels, str):
                node_labels = [[node_labels]] * (len(relationship_types) + 1 if relationship_types else 2)

            if isinstance(relationship_directions, RelationshipDirection):
                relationship_directions = [relationship_directions] * (
                    len(relationship_types) if relationship_types else 1
                )

            if (
                node_labels
                and relationship_types
                and (
                    len(node_labels) != len(relationship_types) + 1
                    or len(relationship_types) != len(relationship_directions)
                )
            ):
                raise ValueError(
                    "number of items in node_labels should be one more than in relationship_types and relationship_directions"
                )

            subgraph_path = f"{CypherNode(variable=ascii_lowercase[0])}"
            for i in range(len(relationship_directions)):
                rel_types = relationship_types[i] if relationship_types else None
                subgraph_path += f"{CypherRelationship(rel_types, relationship_directions[i])}{CypherNode(variable=ascii_lowercase[i + 1])}"

        if subgraph_path is not None:
            self._query.append(ProjectPartialQuery(subgraph_path=subgraph_path, node_labels=node_labels))

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
    def __init__(self, subgraph_path: str, node_labels: Optional[List[List[str]]] = None):
        super().__init__(DeclarativeBaseTypes.MATCH)
        self._subgraph_path = subgraph_path
        self._node_labels = node_labels

    @property
    def subgraph_path(self) -> str:
        return self._subgraph_path

    @property
    def node_labels(self) -> Optional[List[List[str]]]:
        return self._node_labels

    def construct_query(self) -> str:
        """Constructs a Project partial query.

        Given path part of a query (e.g. (:LABEL)-[:TYPE]->(:LABEL2)),
        adds MATCH, a path identifier and appends the WITH clause."""
        query = f" MATCH p={self.subgraph_path}"
        if self.node_labels:
            query += f" WHERE ({ascii_lowercase[0]}:" + f" or {ascii_lowercase[0]}:".join(self.node_labels[0]) + ")"
            for i in range(1, len(self.node_labels)):
                query += f" AND ({ascii_lowercase[i]}:" + f" or {ascii_lowercase[i]}:".join(self.node_labels[i]) + ")"

        return query + " WITH project(p) AS graph "
