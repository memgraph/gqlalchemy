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
from typing import Any, Dict, Iterator, List, Optional, Union, Tuple

from .memgraph import Connection, Memgraph
from .utilities import to_cypher_labels, to_cypher_properties, to_cypher_value
from .models import Node, Relationship


class GTypes:
    NODE = "NODE"
    EDGE = "EDGE"
    MATCH = "MATCH"
    WHERE = "WHERE"
    AND_WHERE = "AND_WHERE"
    OR_WHERE = "OR_WHERE"
    CALL = "CALL"
    RETURN = "RETURN"
    YIELD = "YIELD"
    WITH = "WITH"
    UNWIND = "UNWIND"
    ORDER_BY = "ORDER_BY"
    LIMIT = "LIMIT"


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
        super().__init__(GTypes.MATCH)

        self.optional = optional

    def construct_query(self) -> str:
        if self.optional:
            return f" OPTIONAL MATCH "

        return f" MATCH "


class CallPartialQuery(PartialQuery):
    def __init__(self, procedure: str, arguments: Optional[List[str]]):
        super().__init__(GTypes.CALL)

        self.procedure = procedure
        self._arguments = arguments

    @property
    def arguments(self) -> str:
        return self._arguments if self._arguments is not None else ""

    def construct_query(self) -> str:
        return f" CALL {self.procedure}({''.join( argument + ', ' for argument in self.arguments[:-1]) + self.arguments[-1]}) "


class WhereConditionPartialQuery(PartialQuery):
    def __init__(self, keyword: str, query: str):
        super().__init__(GTypes.WHERE)

        self.keyword = keyword
        self.query = query

    def construct_query(self) -> str:
        return f" {self.keyword} {self.query} "


class NodePartialQuery(PartialQuery):
    def __init__(self, variable: Optional[str], labels: Optional[str], properties: Optional[str]):
        super().__init__(GTypes.NODE)

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
        super().__init__(GTypes.EDGE)

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


class UnwindPartialQuery(PartialQuery):
    def __init__(self, argument: Optional[Tuple[str, str]]):
        super().__init__(GTypes.UNWIND)

        self.argument = argument

    def construct_query(self) -> str:
        if not self.argument:
            return f" UNWIND "
        return f" UNWIND {self.argument[0]} AS {self.argument[1]} "


def dict_to_alias_statement(alias_dict: Dict[str, str]) -> str:
    alias_statement = ""
    dict_item_count = len(alias_dict)
    for i, result in enumerate(alias_dict):
        if alias_dict[result] != "" and alias_dict[result] != result:
            alias_statement += result + " AS " + alias_dict[result]
        else:
            alias_statement += result
        if i < dict_item_count - 1:
            alias_statement += ", "
    return alias_statement


class WithPartialQuery(PartialQuery):
    def __init__(self, results: Optional[Dict[str, str]]):
        super().__init__(GTypes.WITH)

        self._results = results

    @property
    def results(self) -> str:
        return self._results if self._results is not None else ""

    def construct_query(self) -> str:
        if len(self.results) == 0:
            return f" WITH * "
        return f" WITH {dict_to_alias_statement(self.results)} "


class YieldPartialQuery(PartialQuery):
    def __init__(self, results: Optional[Dict[str, str]]):
        super().__init__(GTypes.YIELD)

        self._results = results

    @property
    def results(self) -> str:
        return self._results if self._results is not None else ""

    def construct_query(self) -> str:
        if len(self.results) == 0:
            return f" YIELD * "
        return f" YIELD {dict_to_alias_statement(self.results)} "


class ReturnPartialQuery(PartialQuery):
    def __init__(self, results: Optional[Dict[str, str]]):
        super().__init__(GTypes.RETURN)

        self._results = results

    @property
    def results(self) -> str:
        return self._results if self._results is not None else ""

    def construct_query(self) -> str:
        if len(self.results) == 0:
            return f" RETURN * "
        return f" RETURN {dict_to_alias_statement(self.results)} "


class OrderByPartialQuery(PartialQuery):
    def __init__(self, argument: str, desc: Optional[bool]):
        super().__init__(GTypes.ORDER_BY)

        self.argument = argument
        self.desc = desc

    def construct_query(self) -> str:
        return f" ORDER BY {self.argument} {'DESC' if self.desc else ''} "


class LimitPartialQuery(PartialQuery):
    def __init__(self, limit: int):
        super().__init__(GTypes.LIMIT)

        self.limit = limit

    def construct_query(self) -> str:
        return f" LIMIT {self.limit} "


class G:
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        self._query: List[Any] = []
        self._connection = connection if connection is not None else Memgraph()

    def match(self, optional: bool = False) -> "G":
        self._query.append(MatchPartialQuery(optional))

        return self

    def call(self, procedure: str, arguments: Optional[str] = None) -> "G":
        self._query.append(CallPartialQuery(procedure, arguments))

        return self

    def node(
        self,
        labels: Union[str, List[str], None] = "",
        variable: Optional[str] = None,
        node: Optional["Node"] = None,
        **kwargs,
    ) -> "G":
        if not self._is_linking_valid_with_query(GTypes.NODE):
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
    ) -> "G":
        if not self._is_linking_valid_with_query(GTypes.EDGE):
            raise InvalidMatchChainException()

        if relationship is None:
            labels_str = to_cypher_labels(edge_label)
            properties_str = to_cypher_properties(kwargs)
        else:
            labels_str = to_cypher_labels(relationship._type)
            properties_str = to_cypher_properties(relationship._properties)

        self._query.append(EdgePartialQuery(variable, labels_str, properties_str, bool(directed)))

        return self

    def where(self, property: str, operator: str, value: Any) -> "G":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.WHERE, " ".join([property, operator, value_cypher]))
        )

        return self

    def and_where(self, property: str, operator: str, value: Any) -> "G":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.AND, " ".join([property, operator, value_cypher]))
        )

        return self

    def or_where(self, property: str, operator: str, value: Any) -> "G":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.OR, " ".join([property, operator, value_cypher]))
        )

        return self

    def unwind(self, argument: Optional[Tuple[str, str]] = ()) -> "G":
        self._query.append(UnwindPartialQuery(argument))

        return self

    def with_(self, results: Optional[Dict[str, str]] = {}) -> "G":
        self._query.append(WithPartialQuery(results))

        return self

    def yield_(self, results: Optional[Dict[str, str]] = {}) -> "G":
        self._query.append(YieldPartialQuery(results))

        return self

    def return_(self, results: Optional[Dict[str, str]] = {}) -> "G":
        self._query.append(ReturnPartialQuery(results))

        return self

    def orderby(self, argument: str, sort: Optional[bool] = False) -> "G":
        self._query.append(OrderByPartialQuery(argument, sort))

        return self

    def limit(self, limit: int) -> "G":
        self._query.append(LimitPartialQuery(limit))

        return self

    def get_single(self, retrieve: str) -> Any:
        query = self._construct_query()

        result = next(self._connection.execute_and_fetch(query), None)

        if result:
            return result[retrieve]
        return result

    def execute(self) -> Iterator[Dict[str, Any]]:
        query = self._construct_query()
        return self._connection.execute_and_fetch(query)

    def _construct_query(self) -> str:
        query = [""]

        # if not self._any_variables_matched():
        #    raise NoVariablesMatchedException()

        for partial_query in self._query:
            query.append(partial_query.construct_query())

        joined_query = "".join(query)
        joined_query = re.sub("\\s\\s+", " ", joined_query)
        return joined_query

    def _any_variables_matched(self) -> bool:
        return any(q.type in [GTypes.EDGE, GTypes.NODE] and q.variable not in [None, ""] for q in self._query)

    def _is_linking_valid_with_query(self, match_type: str):
        return len(self._query) == 0 or self._query[-1].type != match_type
