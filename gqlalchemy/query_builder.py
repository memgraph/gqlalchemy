# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Union

from .memgraph import Connection, Memgraph
from .utilities import to_cypher_labels, to_cypher_properties, to_cypher_value
from .models import Node, Relationship


class MatchTypes:
    NODE = "NODE"
    EDGE = "EDGE"
    MATCH = "MATCH"
    WHERE = "WHERE"
    AND_WHERE = "AND_WHERE"
    OR_WHERE = "OR_WHERE"


class MatchConstants:
    DIRECTED = "directed"
    LABELS_STR = "labels_str"
    OPTIONAL = "optional"
    PROPERTIES_STR = "properties_str"
    QUERY = "query"
    TYPE = "type"
    VARIABLE = "variable"


class WhereConditionConstants:
    WHERE = "WHERE"
    AND = "AND"
    OR = "OR"


class NoVariablesMatchedException(Exception):
    def __init__(self):
        message = f"No variables have been matched in the query"
        super().__init__(message)


class InvalidMatchChainException(Exception):
    def __init__(self):
        message = f"Invalid match query when linking!"
        super().__init__(message)


class PartialQuery(ABC):
    def __init__(self, type: str):
        self.type = type

    @abstractmethod
    def construct_query(self) -> str:
        pass


class MatchPartialQuery(PartialQuery):
    def __init__(self, optional: bool):
        super().__init__(MatchTypes.MATCH)

        self.optional = optional

    def construct_query(self) -> str:
        if self.optional:
            return f" OPTIONAL MATCH "

        return f" MATCH "


class WhereConditionPartialQuery(PartialQuery):
    def __init__(self, keyword: str, query: str):
        super().__init__(MatchTypes.WHERE)

        self.keyword = keyword
        self.query = query

    def construct_query(self) -> str:
        return f" {self.keyword} {self.query} "


class NodePartialQuery(PartialQuery):
    def __init__(self, variable: Optional[str], labels: Optional[str], properties: Optional[str]):
        super().__init__(MatchTypes.NODE)

        self._variable = variable
        self._labels = labels
        self._properties = properties

    @property
    def variable(self) -> str:
        return self._variable if self._variable is not None else ""

    @property
    def labels(self) -> str:
        return self._labels if self._labels is not None else ""

    @property
    def properties(self) -> str:
        return self._properties if self._properties is not None else ""

    def construct_query(self) -> str:
        return f"({self.variable}{self.labels}{self.properties})"


class EdgePartialQuery(PartialQuery):
    def __init__(self, variable: Optional[str], labels: Optional[str], properties: Optional[str], directed: bool):
        super().__init__(MatchTypes.EDGE)

        self.directed = directed
        self._variable = variable
        self._labels = labels
        self._properties = properties

    @property
    def variable(self) -> str:
        return self._variable if self._variable is not None else ""

    @property
    def labels(self) -> str:
        return self._labels if self._labels is not None else ""

    @property
    def properties(self) -> str:
        return self._properties if self._properties is not None else ""

    def construct_query(self) -> str:
        relationship_query = f"{self.variable}{self.labels}{self.properties}"
        if self.directed:
            relationship_query = f"-[{relationship_query}]->"
        else:
            relationship_query = f"-[{relationship_query}]-"

        return relationship_query


class Match:
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        self._query: List[Any] = []
        self._connection = connection if connection is not None else Memgraph()

    def match(self, optional: bool = False) -> "Match":
        self._query.append(MatchPartialQuery(optional))

        return self

    def node(
        self,
        labels: Union[str, List[str], None] = "",
        variable: Optional[str] = None,
        node: Optional["Node"] = None,
        **kwargs,
    ) -> "Match":
        if not self._is_linking_valid_with_query(MatchTypes.NODE):
            raise InvalidMatchChainException()

        if node is None:
            labels_str = to_cypher_labels(labels)
            properties_str = to_cypher_properties(kwargs)
        else:
            labels_str = to_cypher_labels(node._labels)
            properties_str = to_cypher_properties(node._properties)

        self._query.append(NodePartialQuery(variable, labels_str, properties_str))

        return self

    def to(
        self,
        edge_label: Optional[str] = "",
        directed: Optional[bool] = True,
        variable: Optional[str] = None,
        relationship: Optional["Relationship"] = None,
        **kwargs,
    ) -> "Match":
        if not self._is_linking_valid_with_query(MatchTypes.EDGE):
            raise InvalidMatchChainException()

        if relationship is None:
            labels_str = to_cypher_labels(edge_label)
            properties_str = to_cypher_properties(kwargs)
        else:
            labels_str = to_cypher_labels(relationship._type)
            properties_str = to_cypher_properties(relationship._properties)

        self._query.append(EdgePartialQuery(variable, labels_str, properties_str, bool(directed)))

        return self

    def where(self, property: str, operator: str, value: Any) -> "Match":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.WHERE, " ".join([property, operator, value_cypher]))
        )

        return self

    def and_where(self, property: str, operator: str, value: Any) -> "Match":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.AND, " ".join([property, operator, value_cypher]))
        )

        return self

    def or_where(self, property: str, operator: str, value: Any) -> "Match":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.OR, " ".join([property, operator, value_cypher]))
        )

        return self

    def get_single(self, retrieve: str) -> Any:
        query = self._construct_query()

        query = f"{query} RETURN {retrieve}"
        result = next(self._connection.execute_and_fetch(query), None)

        if result:
            return result[retrieve]
        return result

    def execute(self) -> Iterator[Dict[str, Any]]:
        query = self._construct_query()
        query = f"{query} RETURN *"

        return self._connection.execute_and_fetch(query)

    def _construct_query(self) -> str:
        query = ["MATCH "]

        if not self._any_variables_matched():
            raise NoVariablesMatchedException()

        for partial_query in self._query:
            query.append(partial_query.construct_query())

        joined_query = "".join(query)
        joined_query = re.sub("\\s\\s+", " ", joined_query)
        return joined_query

    def _any_variables_matched(self) -> bool:
        return any(q.type in [MatchTypes.EDGE, MatchTypes.NODE] and q.variable not in [None, ""] for q in self._query)

    def _is_linking_valid_with_query(self, match_type: str):
        return len(self._query) == 0 or self._query[-1].type != match_type
