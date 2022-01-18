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

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Union

from .memgraph import Connection, Memgraph
from .utilities import to_cypher_labels, to_cypher_properties, to_cypher_value
from .models import Node, Relationship


class DeclarativeBaseTypes:
    AND_WHERE = "AND_WHERE"
    CALL = "CALL"
    CREATE = "CREATE"
    DELETE = "DELETE"
    EDGE = "EDGE"
    LIMIT = "LIMIT"
    MATCH = "MATCH"
    MERGE = "MERGE"
    NODE = "NODE"
    ORDER_BY = "ORDER_BY"
    OR_WHERE = "OR_WHERE"
    REMOVE = "REMOVE"
    RETURN = "RETURN"
    SKIP = "SKIP"
    UNION = "UNION"
    UNWIND = "UNWIND"
    WHERE = "WHERE"
    WITH = "WITH"
    YIELD = "YIELD"


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
        message = "No variables have been matched in the query"
        super().__init__(message)


class InvalidMatchChainException(Exception):
    def __init__(self):
        message = "Invalid match query when linking!"
        super().__init__(message)


class PartialQuery(ABC):
    def __init__(self, type: str):
        self.type = type

    @abstractmethod
    def construct_query(self) -> str:
        pass


class MatchPartialQuery(PartialQuery):
    def __init__(self, optional: bool):
        super().__init__(DeclarativeBaseTypes.MATCH)

        self.optional = optional

    def construct_query(self) -> str:
        if self.optional:
            return " OPTIONAL MATCH "

        return " MATCH "


class MergePartialQuery(PartialQuery):
    def __init__(self):
        super().__init__(DeclarativeBaseTypes.MERGE)

    def construct_query(self) -> str:
        return " MERGE "


class CreatePartialQuery(PartialQuery):
    def __init__(self):
        super().__init__(DeclarativeBaseTypes.CREATE)

    def construct_query(self) -> str:
        return " CREATE "


class CallPartialQuery(PartialQuery):
    def __init__(self, procedure: str, arguments: str):
        super().__init__(DeclarativeBaseTypes.CALL)

        self.procedure = procedure
        self.arguments = arguments

    def construct_query(self) -> str:
        return f" CALL {self.procedure}({self.arguments if self.arguments else ''}) "


class WhereConditionPartialQuery(PartialQuery):
    def __init__(self, keyword: str, query: str):
        super().__init__(DeclarativeBaseTypes.WHERE)

        self.keyword = keyword
        self.query = query

    def construct_query(self) -> str:
        return f" {self.keyword} {self.query} "


class NodePartialQuery(PartialQuery):
    def __init__(self, variable: str, labels: str, properties: str):
        super().__init__(DeclarativeBaseTypes.NODE)

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
    def __init__(
        self, variable: Optional[str], labels: Optional[str], properties: Optional[str], directed: bool, from_: bool
    ):
        super().__init__(DeclarativeBaseTypes.EDGE)

        self.directed = directed
        self._variable = variable
        self._labels = labels
        self._properties = properties
        self._from = from_

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

        if not self.directed:
            relationship_query = f"-[{relationship_query}]-"
            return relationship_query

        if self._from:
            relationship_query = f"<-[{relationship_query}]-"
        else:
            relationship_query = f"-[{relationship_query}]->"

        return relationship_query


class UnwindPartialQuery(PartialQuery):
    def __init__(self, list_expression: str, variable: str):
        super().__init__(DeclarativeBaseTypes.UNWIND)

        self.list_expression = list_expression
        self.variable = variable

    def construct_query(self) -> str:
        return f" UNWIND {self.list_expression} AS {self.variable} "


def dict_to_alias_statement(alias_dict: Dict[str, str]) -> str:
    return ", ".join(
        f"{key} AS {value}" if value != "" and key != value else f"{key}" for (key, value) in alias_dict.items()
    )


class WithPartialQuery(PartialQuery):
    def __init__(self, results: Dict[str, str]):
        super().__init__(DeclarativeBaseTypes.WITH)

        self._results = results

    @property
    def results(self) -> str:
        return self._results if self._results is not None else ""

    def construct_query(self) -> str:
        if len(self.results) == 0:
            return " WITH * "
        return f" WITH {dict_to_alias_statement(self.results)} "


class UnionPartialQuery(PartialQuery):
    def __init__(self, include_duplicates: bool):
        super().__init__(DeclarativeBaseTypes.UNION)

        self.include_duplicates = include_duplicates

    def construct_query(self) -> str:
        return f" UNION{f' ALL' if self.include_duplicates else ''} "


class DeletePartialQuery(PartialQuery):
    def __init__(self, variable_expressions: List[str], detach: bool):
        super().__init__(DeclarativeBaseTypes.DELETE)

        self._variable_expressions = variable_expressions
        self.detach = detach

    @property
    def variable_expressions(self) -> str:
        return self._variable_expressions if self._variable_expressions is not None else ""

    def construct_query(self) -> str:
        return f" {'DETACH' if self.detach else ''} DELETE {', '.join(self.variable_expressions)} "


class RemovePartialQuery(PartialQuery):
    def __init__(self, items: List[str]):
        super().__init__(DeclarativeBaseTypes.REMOVE)

        self._items = items

    @property
    def items(self) -> str:
        return self._items if self._items is not None else ""

    def construct_query(self) -> str:
        return f" REMOVE {', '.join(self.items)} "


class YieldPartialQuery(PartialQuery):
    def __init__(self, results: Dict[str, str]):
        super().__init__(DeclarativeBaseTypes.YIELD)

        self._results = results

    @property
    def results(self) -> str:
        return self._results if self._results is not None else ""

    def construct_query(self) -> str:
        if len(self.results) == 0:
            return " YIELD * "
        return f" YIELD {dict_to_alias_statement(self.results)} "


class ReturnPartialQuery(PartialQuery):
    def __init__(self, results: Dict[str, str]):
        super().__init__(DeclarativeBaseTypes.RETURN)

        self._results = results

    @property
    def results(self) -> str:
        return self._results if self._results is not None else ""

    def construct_query(self) -> str:
        if len(self.results) == 0:
            return " RETURN * "
        return f" RETURN {dict_to_alias_statement(self.results)} "


class OrderByPartialQuery(PartialQuery):
    def __init__(self, properties: str):
        super().__init__(DeclarativeBaseTypes.ORDER_BY)

        self.properties = properties

    def construct_query(self) -> str:
        return f" ORDER BY {self.properties} "


class LimitPartialQuery(PartialQuery):
    def __init__(self, integer_expression: str):
        super().__init__(DeclarativeBaseTypes.LIMIT)

        self.integer_expression = integer_expression

    def construct_query(self) -> str:
        return f" LIMIT {self.integer_expression} "


class SkipPartialQuery(PartialQuery):
    def __init__(self, integer_expression: str):
        super().__init__(DeclarativeBaseTypes.SKIP)

        self.integer_expression = integer_expression

    def construct_query(self) -> str:
        return f" SKIP {self.integer_expression} "


class DeclarativeBase(ABC):
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        self._query: List[Any] = []
        self._connection = connection if connection is not None else Memgraph()

    def match(self, optional: bool = False) -> "DeclarativeBase":
        self._query.append(MatchPartialQuery(optional))

        return self

    def merge(self) -> "DeclarativeBase":
        self._query.append(MergePartialQuery())

        return self

    def create(self) -> "DeclarativeBase":
        self._query.append(CreatePartialQuery())

        return self

    def call(self, procedure: str, arguments: Optional[str] = None) -> "DeclarativeBase":
        self._query.append(CallPartialQuery(procedure, arguments))

        return self

    def node(
        self,
        labels: Union[str, List[str], None] = "",
        variable: Optional[str] = None,
        node: Optional["Node"] = None,
        **kwargs,
    ) -> "DeclarativeBase":
        if not self._is_linking_valid_with_query(DeclarativeBaseTypes.NODE):
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
    ) -> "DeclarativeBase":
        if not self._is_linking_valid_with_query(DeclarativeBaseTypes.EDGE):
            raise InvalidMatchChainException()

        if relationship is None:
            labels_str = to_cypher_labels(edge_label)
            properties_str = to_cypher_properties(kwargs)
        else:
            labels_str = to_cypher_labels(relationship._type)
            properties_str = to_cypher_properties(relationship._properties)

        self._query.append(EdgePartialQuery(variable, labels_str, properties_str, bool(directed), False))

        return self

    def from_(
        self,
        edge_label: Optional[str] = "",
        directed: Optional[bool] = True,
        variable: Optional[str] = None,
        relationship: Optional["Relationship"] = None,
        **kwargs,
    ) -> "Match":
        if not self._is_linking_valid_with_query(DeclarativeBaseTypes.EDGE):
            raise InvalidMatchChainException()

        if relationship is None:
            labels_str = to_cypher_labels(edge_label)
            properties_str = to_cypher_properties(kwargs)
        else:
            labels_str = to_cypher_labels(relationship._type)
            properties_str = to_cypher_properties(relationship._properties)

        self._query.append(EdgePartialQuery(variable, labels_str, properties_str, bool(directed), True))

        return self

    def where(self, property: str, operator: str, value: Any) -> "DeclarativeBase":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.WHERE, " ".join([property, operator, value_cypher]))
        )

        return self

    def and_where(self, property: str, operator: str, value: Any) -> "DeclarativeBase":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.AND, " ".join([property, operator, value_cypher]))
        )

        return self

    def or_where(self, property: str, operator: str, value: Any) -> "DeclarativeBase":
        value_cypher = to_cypher_value(value)
        self._query.append(
            WhereConditionPartialQuery(WhereConditionConstants.OR, " ".join([property, operator, value_cypher]))
        )

        return self

    def unwind(self, list_expression: str, variable: str) -> "DeclarativeBase":
        self._query.append(UnwindPartialQuery(list_expression, variable))

        return self

    def with_(self, results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase":
        self._query.append(WithPartialQuery(results))

        return self

    def union(self, include_duplicates: Optional[bool] = True) -> "DeclarativeBase":
        self._query.append(UnionPartialQuery(include_duplicates))

        return self

    def delete(self, variable_expressions: List[str], detach: Optional[bool] = False) -> "DeclarativeBase":
        self._query.append(DeletePartialQuery(variable_expressions, detach))

        return self

    def remove(self, items: List[str]) -> "DeclarativeBase":
        self._query.append(RemovePartialQuery(items))

        return self

    def yield_(self, results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase":
        self._query.append(YieldPartialQuery(results))

        return self

    def return_(self, results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase":
        self._query.append(ReturnPartialQuery(results))

        return self

    def order_by(self, properties: str) -> "DeclarativeBase":
        self._query.append(OrderByPartialQuery(properties))

        return self

    def limit(self, integer_expression: str) -> "DeclarativeBase":
        self._query.append(LimitPartialQuery(integer_expression))

        return self

    def skip(self, integer_expression: str) -> "DeclarativeBase":
        self._query.append(SkipPartialQuery(integer_expression))

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
        return any(
            q.type in [DeclarativeBaseTypes.EDGE, DeclarativeBaseTypes.NODE] and q.variable not in [None, ""]
            for q in self._query
        )

    def _is_linking_valid_with_query(self, match_type: str):
        return len(self._query) == 0 or self._query[-1].type != match_type


class QueryBuilder(DeclarativeBase):
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)


class Create(DeclarativeBase):
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)
        self._query.append(CreatePartialQuery())


class Match(DeclarativeBase):
    def __init__(self, optional: bool = False, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)
        self._query.append(MatchPartialQuery(optional))


class Merge(DeclarativeBase):
    def __init__(self, optional: bool = False, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)
        self._query.append(MergePartialQuery(optional))


class Call(DeclarativeBase):
    def __init__(
        self, procedure: str, arguments: Optional[str] = None, connection: Optional[Union[Connection, Memgraph]] = None
    ):
        super().__init__(connection)
        self._query.append(CallPartialQuery(procedure, arguments))


class Unwind(DeclarativeBase):
    def __init__(self, list_expression: str, variable: str, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)
        self._query.append(UnwindPartialQuery(list_expression, variable))


class With(DeclarativeBase):
    def __init__(
        self, results: Optional[Dict[str, str]] = {}, connection: Optional[Union[Connection, Memgraph]] = None
    ):
        super().__init__(connection)
        self._query.append(WithPartialQuery(results))
