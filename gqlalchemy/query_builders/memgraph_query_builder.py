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

from typing import Optional

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


class LoadCsv(DeclarativeBase):
    def __init__(self, path: str, header: bool, row: str, connection: Optional[DatabaseClient] = None):
        super().__init__(connection)
        self._query.append(LoadCsvPartialQuery(path, header, row))
