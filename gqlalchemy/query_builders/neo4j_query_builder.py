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

from .declarative_base import DeclarativeBase, Call, Create, Match, Merge, Return, Unwind, With  # noqa F401
from ..vendors.neo4j import Neo4j


class Neo4jQueryBuilder(DeclarativeBase):
    def __init__(self, connection: Neo4j):
        super().__init__(connection)


def load_csv(**kwargs) -> None:
    raise NotImplementedError


def LoadCsv(**kwargs) -> None:
    raise NotImplementedError