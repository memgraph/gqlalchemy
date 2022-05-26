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

from enum import Enum
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from .memgraph import Connection, Memgraph
from .graph_algorithms.integrated_algorithms import IntegratedAlgorithm
from .utilities import to_cypher_labels, to_cypher_properties, to_cypher_value
from .models import Node, Relationship
from .exceptions import (
    GQLAlchemyExtraKeywordArgumentsInSet,
    GQLAlchemyLiteralAndExpressionMissingInWhere,
    GQLAlchemyLiteralAndExpressionMissingInSet,
    GQLAlchemyExtraKeywordArgumentsInWhere,
    GQLAlchemyMissingOrder,
    GQLAlchemyOrderByTypeError,
)


class DeclarativeBaseTypes:
    CALL = "CALL"
    CREATE = "CREATE"
    DELETE = "DELETE"
    FOREACH = "FOREACH"
    RELATIONSHIP = "RELATIONSHIP"
    LIMIT = "LIMIT"
    LOAD_CSV = "LOAD_CSV"
    MATCH = "MATCH"
    MERGE = "MERGE"
    NODE = "NODE"
    ORDER_BY = "ORDER BY"
    REMOVE = "REMOVE"
    RETURN = "RETURN"
    SET = "SET"
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


class Where(Enum):
    WHERE = 1
    AND = 2
    OR = 3
    XOR = 4
    NOT = 5


class Order(Enum):
    ASC = 1
    ASCENDING = 2
    DESC = 3
    DESCENDING = 4


class SetOperator(Enum):
    ASSIGNMENT = "="
    INCREMENT = "+="
    LABEL_FILTER = ":"


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


class LoadCsvPartialQuery(PartialQuery):
    def __init__(self, path: str, header: bool, row: str):
        super().__init__(DeclarativeBaseTypes.LOAD_CSV)
        self.path = path
        self.header = header
        self.row = row

    def construct_query(self) -> str:
        return f" LOAD CSV FROM '{self.path}' " + ("WITH" if self.header else "NO") + f" HEADER AS {self.row} "


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
    _LITERAL = "literal"
    _EXPRESSION = "expression"
    _LABEL_FILTER = ":"

    def __init__(self, item: str, operator: str, keyword: Where = Where.WHERE, is_negated: bool = False, **kwargs):
        super().__init__(type=keyword.name if not is_negated else f"{keyword.name} {Where.NOT.name}")
        self.query = self._build_where_query(item=item, operator=operator, **kwargs)

    def construct_query(self) -> str:
        """Constructs a where partial query."""
        return f" {self.type} {self.query} "

    def _build_where_query(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Builds parts of a WHERE Cypher query divided by the boolean operators."""
        literal = kwargs.get(WhereConditionPartialQuery._LITERAL)
        value = kwargs.get(WhereConditionPartialQuery._EXPRESSION)

        if value is None:
            if literal is None:
                raise GQLAlchemyLiteralAndExpressionMissingInWhere

            value = to_cypher_value(literal)
        elif literal is not None:
            raise GQLAlchemyExtraKeywordArgumentsInWhere

        return ("" if operator == WhereConditionPartialQuery._LABEL_FILTER else " ").join([item, operator, value])


class WhereNotConditionPartialQuery(WhereConditionPartialQuery):
    def __init__(self, item: str, operator: str, keyword: Where = Where.WHERE, **kwargs):
        super().__init__(item=item, operator=operator, keyword=keyword, is_negated=True, **kwargs)


class AndWhereConditionPartialQuery(WhereConditionPartialQuery):
    def __init__(self, item: str, operator: str, **kwargs):
        super().__init__(item=item, operator=operator, keyword=Where.AND, **kwargs)


class AndNotWhereConditionPartialQuery(WhereNotConditionPartialQuery):
    def __init__(self, item: str, operator: str, **kwargs):
        super().__init__(item=item, operator=operator, keyword=Where.AND, **kwargs)


class OrWhereConditionPartialQuery(WhereConditionPartialQuery):
    def __init__(self, item: str, operator: str, **kwargs):
        super().__init__(item=item, operator=operator, keyword=Where.OR, **kwargs)


class OrNotWhereConditionPartialQuery(WhereNotConditionPartialQuery):
    def __init__(self, item: str, operator: str, **kwargs):
        super().__init__(item=item, operator=operator, keyword=Where.OR, **kwargs)


class XorWhereConditionPartialQuery(WhereConditionPartialQuery):
    def __init__(self, item: str, operator: str, **kwargs):
        super().__init__(item=item, operator=operator, keyword=Where.XOR, **kwargs)


class XorNotWhereConditionPartialQuery(WhereNotConditionPartialQuery):
    def __init__(self, item: str, operator: str, **kwargs):
        super().__init__(item=item, operator=operator, keyword=Where.XOR, **kwargs)


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
        """Constructs a node partial query."""
        return f"({self.variable}{self.labels}{' ' + self.properties if self.properties else ''})"


class RelationshipPartialQuery(PartialQuery):
    def __init__(
        self,
        variable: Optional[str],
        labels: Optional[str],
        algorithm: Optional[str],
        properties: Optional[str],
        directed: bool,
        from_: bool,
    ):
        super().__init__(DeclarativeBaseTypes.RELATIONSHIP)

        self.directed = directed
        self._variable = variable
        self._labels = labels
        self._algorithm = algorithm
        self._properties = properties
        self._from = from_

    @property
    def variable(self) -> str:
        return "" if self._variable is None else self._variable

    @property
    def labels(self) -> str:
        return "" if self._labels is None else self._labels

    @property
    def algorithm(self) -> str:
        return "" if self._algorithm is None else self._algorithm

    @property
    def properties(self) -> str:
        return "" if self._properties is None else self._properties

    def construct_query(self) -> str:
        """Constructs an relationship partial query."""
        relationship_query = f"{self.variable}{self.labels}{self.algorithm}{self.properties}"

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
        """Constructs an unwind partial query."""
        return f" UNWIND {self.list_expression} AS {self.variable} "


def dict_to_alias_statement(alias_dict: Dict[str, str]) -> str:
    """Creates a string expression of alias statements from a dictionary of
    expression, variable name dictionary.
    """
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
        """Creates a WITH statement Cypher partial query."""
        if len(self.results) == 0:
            return " WITH * "
        return f" WITH {dict_to_alias_statement(self.results)} "


class UnionPartialQuery(PartialQuery):
    def __init__(self, include_duplicates: bool):
        super().__init__(DeclarativeBaseTypes.UNION)

        self.include_duplicates = include_duplicates

    def construct_query(self) -> str:
        """Creates a UNION statement Cypher partial query."""
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
        """Creates a DELETE statement Cypher partial query."""
        return f" {'DETACH' if self.detach else ''} DELETE {', '.join(self.variable_expressions)} "


class RemovePartialQuery(PartialQuery):
    def __init__(self, items: List[str]):
        super().__init__(DeclarativeBaseTypes.REMOVE)

        self._items = items

    @property
    def items(self) -> str:
        return self._items if self._items is not None else ""

    def construct_query(self) -> str:
        """Creates a REMOVE statement Cypher partial query."""
        return f" REMOVE {', '.join(self.items)} "


class YieldPartialQuery(PartialQuery):
    def __init__(self, results: Dict[str, str]):
        super().__init__(DeclarativeBaseTypes.YIELD)

        self._results = results

    @property
    def results(self) -> str:
        return self._results if self._results is not None else ""

    def construct_query(self) -> str:
        """Creates a YIELD statement Cypher partial query."""
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
        """Creates a RETURN statement Cypher partial query."""
        if len(self.results) == 0:
            return " RETURN * "
        return f" RETURN {dict_to_alias_statement(self.results)} "


class OrderByPartialQuery(PartialQuery):
    def __init__(self, properties: Union[str, Tuple[str, Order], List[Union[str, Tuple[str, Order]]]]):
        super().__init__(DeclarativeBaseTypes.ORDER_BY)

        self.query = (
            self._order_by_read_list(properties)
            if isinstance(properties, list)
            else self._order_by_read_item(properties)
        )

    def construct_query(self) -> str:
        """Creates a ORDER BY statement Cypher partial query."""
        return f" {self.type} {self.query} "

    def _order_by_read_item(self, item: Union[str, Tuple[str, Order]]) -> str:
        if isinstance(item, str):
            return f"{self._order_by_read_str(item)}"
        elif isinstance(item, tuple):
            return f"{self._order_by_read_tuple(item)}"
        else:
            raise GQLAlchemyOrderByTypeError

    def _order_by_read_list(self, property: List[Union[str, Tuple[str, Order]]]):
        return ", ".join(self._order_by_read_item(item=item) for item in property)

    def _order_by_read_str(self, property: str) -> str:
        return f"{property}"

    def _order_by_read_tuple(self, tuple: Tuple[str, Order]) -> str:
        if not isinstance(tuple[1], Order):
            raise GQLAlchemyMissingOrder

        return f"{tuple[0]} {tuple[1].name}"


class LimitPartialQuery(PartialQuery):
    def __init__(self, integer_expression: str):
        super().__init__(DeclarativeBaseTypes.LIMIT)

        self.integer_expression = integer_expression

    def construct_query(self) -> str:
        """Creates a LIMIT statement Cypher partial query."""
        return f" LIMIT {self.integer_expression} "


class SkipPartialQuery(PartialQuery):
    def __init__(self, integer_expression: str):
        super().__init__(DeclarativeBaseTypes.SKIP)

        self.integer_expression = integer_expression

    def construct_query(self) -> str:
        """Creates a SKIP statement Cypher partial query."""
        return f" SKIP {self.integer_expression} "


class AddStringPartialQuery(PartialQuery):
    def __init__(self, custom_cypher: str):
        super().__init__(DeclarativeBaseTypes.SKIP)

        self.custom_cypher = custom_cypher

    def construct_query(self) -> str:
        return f"{self.custom_cypher}"


class ForeachPartialQuery(PartialQuery):
    def __init__(self, variable: str, expression: str, update_clauses: str):
        super().__init__(DeclarativeBaseTypes.FOREACH)
        self._variable = variable
        self._expression = expression
        self._update_clauses = update_clauses

    @property
    def variable(self) -> str:
        return self._variable if self._variable is not None else ""

    @property
    def expression(self) -> str:
        return self._expression if self._expression is not None else ""

    @property
    def update_clauses(self) -> str:
        return self._update_clauses if self._update_clauses is not None else ""

    def construct_query(self) -> str:
        """Creates a FOREACH statement Cypher partial query."""
        return f" FOREACH ( {self.variable} IN {self.expression} | {self.update_clauses} ) "


class SetPartialQuery(PartialQuery):
    _LITERAL = "literal"
    _EXPRESSION = "expression"

    def __init__(self, item: str, operator: SetOperator, **kwargs):
        super().__init__(DeclarativeBaseTypes.SET)

        self.query = self._build_set_query(item=item, operator=operator, **kwargs)

    def construct_query(self) -> str:
        """Constructs a set partial query."""
        return f" {self.type} {self.query}"

    def _build_set_query(self, item: str, operator: SetOperator, **kwargs) -> "DeclarativeBase":
        """Builds parts of a SET Cypher query divided by the boolean operators."""
        literal = kwargs.get(SetPartialQuery._LITERAL)
        value = kwargs.get(SetPartialQuery._EXPRESSION)

        if value is None:
            if literal is None:
                raise GQLAlchemyLiteralAndExpressionMissingInSet

            value = to_cypher_value(literal)
        elif literal is not None:
            raise GQLAlchemyExtraKeywordArgumentsInSet

        return ("" if operator == SetOperator.LABEL_FILTER else " ").join([item, operator.value, value])


class DeclarativeBase(ABC):
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        self._query: List[PartialQuery] = []
        self._connection = connection if connection is not None else Memgraph()
        self._fetch_results: bool = False

    def match(self, optional: bool = False) -> "DeclarativeBase":
        """Obtain data from the database by matching it to a given pattern.

        Args:
            optional: A bool indicating if missing parts of the pattern will be
            filled with null values.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(MatchPartialQuery(optional))

        return self

    def merge(self) -> "DeclarativeBase":
        """Ensure that a pattern you are looking for exists in the database.
        This means that if the pattern is not found, it will be created. In a
        way, this clause is like a combination of MATCH and CREATE.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(MergePartialQuery())

        return self

    def create(self) -> "DeclarativeBase":
        """Create nodes and relationships in a graph.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(CreatePartialQuery())

        return self

    def call(self, procedure: str, arguments: Optional[str] = None) -> "DeclarativeBase":
        """Call a query module procedure.

        Args:
            procedure: A string representing the name of the procedure in the
              format `query_module.procedure`.
            arguments: A string representing the arguments of the procedure in
              text format.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(CallPartialQuery(procedure, arguments))

        return self

    def node(
        self,
        labels: Union[str, List[str], None] = "",
        variable: Optional[str] = None,
        node: Optional["Node"] = None,
        **kwargs,
    ) -> "DeclarativeBase":
        """Add a node pattern to the query.

        Args:
            labels: A string or list of strings representing the labels of the
              node.
            variable: A string representing the name of the variable for storing
              results of the node pattern.
            node: A `Node` object to construct the pattern from.
            **kwargs: Arguments representing the properties of the node.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
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
        relationship_type: Optional[str] = "",
        directed: Optional[bool] = True,
        variable: Optional[str] = None,
        relationship: Optional["Relationship"] = None,
        algorithm: Optional[IntegratedAlgorithm] = None,
        **kwargs,
    ) -> "DeclarativeBase":
        """Add a relationship pattern to the query.

        Args:
            relationship_type: A string representing the type of the relationship.
            directed: A bool indicating if the relationship is directed.
            variable: A string representing the name of the variable for storing
              results of the relationship pattern.
            relationship: A `Relationship` object to construct the pattern from.
            algorithm: algorithm object to use over graph data.
            **kwargs: Arguments representing the properties of the relationship.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        if not self._is_linking_valid_with_query(DeclarativeBaseTypes.RELATIONSHIP):
            raise InvalidMatchChainException()

        if relationship is None:
            type_str = to_cypher_labels(relationship_type)
            properties_str = to_cypher_properties(kwargs)
        else:
            type_str = to_cypher_labels(relationship._type)
            properties_str = to_cypher_properties(relationship._properties)

        self._query.append(
            RelationshipPartialQuery(
                variable=variable,
                labels=type_str,
                algorithm="" if algorithm is None else str(algorithm),
                properties=properties_str,
                directed=bool(directed),
                from_=False,
            )
        )

        return self

    def from_(
        self,
        relationship_type: Optional[str] = "",
        directed: Optional[bool] = True,
        variable: Optional[str] = None,
        relationship: Optional["Relationship"] = None,
        algorithm: Optional[IntegratedAlgorithm] = None,
        **kwargs,
    ) -> "Match":
        """Add a relationship pattern to the query.

        Args:
            relationship_type: A string representing the type of the relationship.
            directed: A bool indicating if the relationship is directed.
            variable: A string representing the name of the variable for storing
              results of the relationship pattern.
            relationship: A `Relationship` object to construct the pattern from.
            **kwargs: Arguments representing the properties of the relationship.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        if not self._is_linking_valid_with_query(DeclarativeBaseTypes.RELATIONSHIP):
            raise InvalidMatchChainException()

        if relationship is None:
            type_str = to_cypher_labels(relationship_type)
            properties_str = to_cypher_properties(kwargs)
        else:
            type_str = to_cypher_labels(relationship._type)
            properties_str = to_cypher_properties(relationship._properties)

        self._query.append(
            RelationshipPartialQuery(
                variable=variable,
                labels=type_str,
                algorithm="" if algorithm is None else str(algorithm),
                properties=properties_str,
                directed=bool(directed),
                from_=True,
            )
        )

        return self

    def where(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates a WHERE statement Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Raises:
            GQLAlchemyLiteralAndExpressionMissingInWhere: Raises an error when neither literal nor expression keyword arguments were provided.
            GQLAlchemyExtraKeywordArgumentsInWhere: Raises an error when both literal and expression keyword arguments were provided.

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by the equality of `name` properties of two connected nodes.

            Python: `match().node(variable="n").to().node(variable="m").where(item="n.name", operator="=", expression="m.name").return_()`
            Cypher: `MATCH (n)-[]->(m) WHERE n.name = m.name RETURN *;`

            Filtering query results by the node label.

            Python: `match().node(variable="n").where(item="n", operator=":", expression="User").return_()`
            Cypher: `MATCH (n) WHERE n:User RETURN *;`

            Filtering query results by the comparison of node property and literal.

            Python: `match().node(variable="n").where(item="n.age", operator=">", literal=18).return_()`
            Cypher: `MATCH (n) WHERE n.age > 18 RETURN *;`
        """
        # WHERE item operator (literal | expression)
        # item: variable | property
        # expression: label | property
        self._query.append(WhereConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def where_not(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates a WHERE NOT statement Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Raises:
            GQLAlchemyLiteralAndExpressionMissingInWhere: Raises an error when neither literal nor expression keyword arguments were provided.
            GQLAlchemyExtraKeywordArgumentsInWhere: Raises an error when both literal and expression keyword arguments were provided.

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by the equality of `name` properties of two connected nodes.

            Python: `match().node(variable="n").to().node(variable="m").where_not(item="n.name", operator="=", expression="m.name").return_()`
            Cypher: `MATCH (n)-[]->(m) WHERE NOT n.name = m.name RETURN *;`
        """
        self._query.append(WhereNotConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def and_where(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates an AND statement as a part of WHERE Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by node label or the comparison of node property and literal.

            Python: `match().node(variable="n").where(item="n", operator=":", expression="User").and_where(item="n.age", operator=">", literal=18).return_()`
            Cypher: `MATCH (n) WHERE n:User AND n.age > 18 RETURN *;`
        """
        self._query.append(AndWhereConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def and_not_where(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates an AND NOT statement as a part of WHERE Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by node label or the comparison of node property and literal.

            Python: `match().node(variable="n").where(item="n", operator=":", expression="User").and_not_where(item="n.age", operator=">", literal=18).return_()`
            Cypher: `MATCH (n) WHERE n:User AND NOT n.age > 18 RETURN *;`
        """
        self._query.append(AndNotWhereConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def or_where(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates an OR statement as a part of WHERE Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by node label or the comparison of node property and literal.

            Python: `match().node(variable="n").where(item="n", operator=":", expression="User").or_where(item="n.age", operator=">", literal=18).return_()`
            Cypher: `MATCH (n) WHERE n:User OR n.age > 18 RETURN *;`
        """
        self._query.append(OrWhereConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def or_not_where(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates an OR NOT statement as a part of WHERE Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by node label or the comparison of node property and literal.

            Python: `match().node(variable="n").where(item="n", operator=":", expression="User").or_not_where(item="n.age", operator=">", literal=18).return_()`
            Cypher: `MATCH (n) WHERE n:User OR NOT n.age > 18 RETURN *;`
        """
        self._query.append(OrNotWhereConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def xor_where(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates an XOR statement as a part of WHERE Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by node label or the comparison of node property and literal.

            Python: `match().node(variable="n").where(item="n", operator=":", expression="User").xor_where(item="n.age", operator=">", literal=18).return_()`
            Cypher: `MATCH (n) WHERE n:User XOR n.age > 18 RETURN *;`
        """
        self._query.append(XorWhereConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def xor_not_where(self, item: str, operator: str, **kwargs) -> "DeclarativeBase":
        """Creates an XOR NOT statement as a part of WHERE Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: A string representing the operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Filtering query results by node label or the comparison of node property and literal.

            Python: `match().node(variable="n").where(item="n", operator=":", expression="User").xor_not_where(item="n.age", operator=">", literal=18).return_()`
            Cypher: `MATCH (n) WHERE n:User XOR NOT n.age > 18 RETURN *;`
        """
        self._query.append(XorNotWhereConditionPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def unwind(self, list_expression: str, variable: str) -> "DeclarativeBase":
        """Unwind a list of values as individual rows.

        Args:
            list_expression: A list of strings representing the list of values.
            variable: A string representing the variable name for unwinding results.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(UnwindPartialQuery(list_expression, variable))

        return self

    def with_(self, results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase":
        """Chain together parts of a query, piping the results from one to be
        used as starting points or criteria in the next.

        Args:
            results: A dictionary mapping variables in the first query with
            aliases in the second query.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(WithPartialQuery(results))

        return self

    def union(self, include_duplicates: Optional[bool] = True) -> "DeclarativeBase":
        """Combine the result of multiple queries.

        Args:
            include_duplicates: A bool indicating if duplicates should be
              included.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(UnionPartialQuery(include_duplicates))

        return self

    def delete(self, variable_expressions: List[str], detach: Optional[bool] = False) -> "DeclarativeBase":
        """Delete nodes and relationships from the database.

        Args:
            variable_expressions: A list of strings indicating which nodes
              and/or relationships should be removed.
            detach: A bool indicating if relationships should be deleted along
              with a node.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(DeletePartialQuery(variable_expressions, detach))

        return self

    def remove(self, items: List[str]) -> "DeclarativeBase":
        """Remove labels and properties from nodes and relationships.

        Args:
            items: A list of strings indicating which labels and/or properties
              should be removed.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(RemovePartialQuery(items))

        return self

    def yield_(self, results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase":
        """Yield data from the query.

        Args:
            results: A dictionary mapping items that are returned with alias
              names.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(YieldPartialQuery(results))

        return self

    def return_(self, results: Optional[Dict[str, str]] = {}) -> "DeclarativeBase":
        """Return data from the query.

        Args:
            results: A dictionary mapping items that are returned with alias
              names.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(ReturnPartialQuery(results))
        self._fetch_results = True

        return self

    def order_by(
        self, properties: Union[str, Tuple[str, Order], List[Union[str, Tuple[str, Order]]]]
    ) -> "DeclarativeBase":
        """Creates an ORDER BY statement Cypher partial query.

        Args:
            properties: Properties and order by which the query results will be ordered.

        Raises:
            GQLAlchemyOrderByTypeError: Raises an error when the given ordering is of the wrong type.
            GQLAlchemyMissingOrdering: Raises an error when the given property is neither string nor tuple.

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Ordering query results by the property `n.name` in ascending order
            and by the property `n.last_name` in descending order:

            Python: `match().node(variable="n").return_().order_by(properties=["n.name", ("n.last_name", Order.DESC)])`
            Cypher: `MATCH (n) RETURN * ORDER BY n.name, n.last_name DESC;`
        """
        self._query.append(OrderByPartialQuery(properties=properties))

        return self

    def limit(self, integer_expression: str) -> "DeclarativeBase":
        """Limit the number of records when returning results.

        Args:
            integer_expression: An integer indicating how many records to limit
              the results to.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(LimitPartialQuery(integer_expression))

        return self

    def skip(self, integer_expression: str) -> "DeclarativeBase":
        """Skip a number of records when returning results.

        Args:
            integer_expression: An integer indicating how many records to skip
              in the results.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(SkipPartialQuery(integer_expression))

        return self

    def add_custom_cypher(self, custom_cypher: str) -> "DeclarativeBase":
        """Inject custom Cypher code into the query.

        Args:
            custom_cypher: A string representing the Cypher code to be injected
              into the query.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(AddStringPartialQuery(custom_cypher))
        if " RETURN " in custom_cypher:
            self._fetch_results = True

        return self

    def load_csv(self, path: str, header: bool, row: str) -> "DeclarativeBase":
        """Load data from a CSV file by executing a Cypher query for each row.

        Args:
            path: A string representing the path to the CSV file.
            header: A bool indicating if the CSV file starts with a header row.
            row: A string representing the name of the variable for iterating
              over each row.

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        self._query.append(LoadCsvPartialQuery(path, header, row))

        return self

    def get_single(self, retrieve: str) -> Any:
        """Returns a single result with a `retrieve` variable name.

        Args:
            retrieve: A string representing the results variable to be returned.

        Returns:
            An iterator of dictionaries containing the results of the query.
        """
        query = self._construct_query()

        result = next(self._connection.execute_and_fetch(query), None)

        if result:
            return result[retrieve]
        return result

    def foreach(self, variable: str, expression: str, update_clauses: Union[str, List[str]]) -> "DeclarativeBase":
        """Iterate over a list of elements and for every iteration run every update clause.

        Args:
            variable: variable name that stores each element
            expression: Any expression that results to a list
            update_clauses: One or more Cypher update clauses:
                SET, REMOVE, CREATE, MERGE, DELETE, FOREACH

        Returns:
            A `DeclarativeBase` instance for constructing queries.
        """
        if isinstance(update_clauses, list):
            update_clauses = " ".join(update_clauses)

        self._query.append(ForeachPartialQuery(variable, expression, update_clauses))

        return self

    def set_(self, item: str, operator: SetOperator, **kwargs):
        """Creates a SET statement Cypher partial query.

        Args:
            item: A string representing variable or property.
            operator: An assignment, increment or label filter operator.

        Kwargs:
            literal: A value that will be converted to Cypher value, such as int, float, string, etc.
            expression: A node label or property that won't be converted to Cypher value (no additional quotes will be added).

        Raises:
            GQLAlchemyLiteralAndExpressionMissingInWhere: Raises an error when neither literal nor expression keyword arguments were provided.
            GQLAlchemyExtraKeywordArgumentsInWhere: Raises an error when both literal and expression keyword arguments were provided.

        Returns:
            self: A partial Cypher query built from the given parameters.

        Examples:
            Setting or updating a property.

            Python: `match().node(variable="n").where(item="n.name", operator="=", literal="Germany").set_(item="n.population", operator=SetOperator.ASSIGNMENT, literal=83000001).return_()`
            Cypher: `MATCH (n) WHERE n.name = 'Germany' SET n.population = 83000001 RETURN *;`

            Setting or updating multiple properties.

            Python: `match().node(variable="n").where(item="n.name", operator="=", literal="Germany").set_(item="n.population", operator=SetOperator.ASSIGNMENT, literal=83000001).set_(item="n.capital", operator=SetOperator.ASSIGNMENT, literal="Berlin").return_()`
            Cypher: `MATCH (n) WHERE n.name = 'Germany' SET n.population = 83000001 SET n.capital = 'Berlin' RETURN *;`

            Setting node label.

            Python: `match().node(variable="n").where(item="n.name", operator="=", literal="Germany").set_(item="n", operator=SetOperator.LABEL_FILTER, expression="Land").return_()`
            Cypher: `MATCH (n) WHERE n.name = 'Germany' SET n:Land RETURN *;`

            Setting or updating all properties using map.

            Python: `match().node(variable="c", labels="Country").where(item="c.name", operator="=", literal="Germany").set_(item="c", operator=SetOperator.INCREMENT, literal={"name": "Germany", "population": "85000000"}).return_()`
            Cypher: `MATCH (c:Country) WHERE c.name = 'Germany' SET c += {name: 'Germany', population: '85000000'} RETURN *;`

        """
        self._query.append(SetPartialQuery(item=item, operator=operator, **kwargs))

        return self

    def execute(self) -> Iterator[Dict[str, Any]]:
        """Executes the Cypher query and returns the results.

        Returns:
            An iterator of dictionaries containing the results of the query.
        """
        query = self._construct_query()
        if self._fetch_results:
            return self._connection.execute_and_fetch(query)
        else:
            return self._connection.execute(query)

    def _construct_query(self) -> str:
        """Constructs the (partial) Cypher query so it can be executed."""
        query = [""]

        # if not self._any_variables_matched():
        #    raise NoVariablesMatchedException()

        for partial_query in self._query:
            query.append(partial_query.construct_query())

        joined_query = "".join(query)
        joined_query = re.sub("\\s\\s+", " ", joined_query)
        return joined_query

    def construct_query(self) -> str:
        return self._construct_query()

    def _any_variables_matched(self) -> bool:
        """Checks if any variables are present in the result."""
        return any(
            q.type in [DeclarativeBaseTypes.RELATIONSHIP, DeclarativeBaseTypes.NODE] and q.variable not in [None, ""]
            for q in self._query
        )

    def _is_linking_valid_with_query(self, match_type: str):
        """Checks if linking functions match the current query."""
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
    def __init__(self, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)
        self._query.append(MergePartialQuery())


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


class Foreach(DeclarativeBase):
    def __init__(
        self,
        variable: str,
        expression: str,
        update_clauses: Union[str, List[str]],
        connection: Optional[Union[Connection, Memgraph]] = None,
    ):
        super().__init__(connection)
        self._query.append(ForeachPartialQuery(variable, expression, update_clauses))


class LoadCsv(DeclarativeBase):
    def __init__(self, path: str, header: bool, row: str, connection: Optional[Union[Connection, Memgraph]] = None):
        super().__init__(connection)
        self._query.append(LoadCsvPartialQuery(path, header, row))


class Return(DeclarativeBase):
    def __init__(
        self, results: Optional[Dict[str, str]] = {}, connection: Optional[Union[Connection, Memgraph]] = None
    ):
        super().__init__(connection)
        self._query.append(ReturnPartialQuery(results))
        self._fetch_results = True
