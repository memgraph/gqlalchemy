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

from .disk_storage import SQLitePropertyDatabase  # noqa F401
from .exceptions import GQLAlchemyWarning, GQLAlchemyError  # noqa F401
from .instance_runner import (  # noqa F401
    DockerImage,
    MemgraphInstanceBinary,
    MemgraphInstanceDocker,
    wait_for_docker_container,
    wait_for_port,
)
from .models import (  # noqa F401
    MemgraphConstraintExists,
    MemgraphConstraintUnique,
    MemgraphIndex,
    MemgraphKafkaStream,
    MemgraphPulsarStream,
    MemgraphTrigger,
    Neo4jConstraintUnique,
    Neo4jIndex,
    Node,
    Path,
    Relationship,
    Field,
)
from .query_builders import (  # noqa F401
    neo4j_query_builder,
    memgraph_query_builder,
    memgraph_query_builder as query_builder,
)
from .query_builders.declarative_base import (  # noqa F401
    Call,
    Create,
    Foreach,
    InvalidMatchChainException,
    Return,
    Match,
    Merge,
    NoVariablesMatchedException,
    Unwind,
    With,
)
from .query_builders.memgraph_query_builder import LoadCsv, QueryBuilder
from .query_builders.neo4j_query_builder import Neo4jQueryBuilder  # noqa F401
from .vendors.memgraph import Memgraph  # noqa F401
from .vendors.neo4j import Neo4j  # noqa F401

from pydantic import validator  # noqa F401
import warnings

warnings.filterwarnings("once", category=GQLAlchemyWarning)
__all__ = ["Memgraph"]

call = Call
create = Create
match = Match
merge = Merge
unwind = Unwind
with_ = With
foreach = Foreach
return_ = Return
load_csv = LoadCsv
MemgraphQueryBuilder = QueryBuilder
