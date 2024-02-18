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

from abc import ABC, abstractmethod

BFS_EXPANSION = " *BFS"
DFS_EXPANSION = " *"
WSHORTEST_EXPANSION = " *WSHORTEST"
ALLSHORTEST_EXPANSION = " *ALLSHORTEST"

DEFAULT_TOTAL_WEIGHT = "total_weight"
DEFAULT_WEIGHT_PROPERTY = "r.weight"


class IntegratedAlgorithm(ABC):
    """Abstract class modeling Memgraph's built-in graph algorithms.

    These algorithms are integrated into Memgraph's codebase and are called
    within a relationship part of a query. For instance:
    MATCH p = (:City {name: "Paris"})
          -[:Road * bfs (r, n | r.length <= 200 AND n.name != "Metz")]->
          (:City {name: "Berlin"})
    """

    @abstractmethod
    def __str__(self) -> str:
        """Instance of IntegratedAlgorithm subclass is used as a string"""
        pass

    @staticmethod
    def to_cypher_lambda(expression: str) -> str:
        """Method for creating a general lambda expression.

        Variables `r` and `n` stand for relationship and node. The expression is
        used e.g. for a filter lambda, to use only relationships of length less
        than 200:
            expression="r.length < 200"
        with the filter lambda being:
            (r, n | r.length < 200)

        Args:
            expression: Lambda conditions or statements.
        """
        return "" if expression is None else f"(r, n | {expression})"


class BreadthFirstSearch(IntegratedAlgorithm):
    """Build a BFS call for a Cypher query.

    The Breadth-first search can be called in Memgraph with Cypher queries such
    as: `MATCH (a {id: 723})-[*BFS ..10 (r, n | r.x > 12 AND n.y < 3)]-() RETURN *;`
    It is called inside the relationship clause, `*BFS` naming the algorithm,
    `..10` specifying depth bounds, and `(r, n | <expression>)` is a filter
    lambda.
    """

    def __init__(
        self,
        lower_bound: int = None,
        upper_bound: int = None,
        condition: str = None,
    ) -> None:
        """
        Args:
            lower_bound: Lower bound for path depth.
            upper_bound: Upper bound for path depth.
            condition: Filter through nodes and relationships that pass this
            condition.
        """
        super().__init__()
        self.lower_bound = str(lower_bound) if lower_bound is not None else ""
        self.upper_bound = str(upper_bound) if upper_bound is not None else ""
        self.condition = condition

    def __str__(self) -> str:
        """Get a Cypher query string for this algorithm."""
        algo_str = BFS_EXPANSION

        bounds = self.to_cypher_bounds()
        if bounds != "":
            algo_str = f"{algo_str} {bounds}"

        filter_lambda = super().to_cypher_lambda(self.condition)
        if filter_lambda != "":
            algo_str = f"{algo_str} {filter_lambda}"

        return algo_str

    def to_cypher_bounds(self) -> str:
        """If bounds are specified, returns them in grammar-defined form."""
        if self.lower_bound == "" and self.upper_bound == "":
            return ""

        return f"{self.lower_bound}..{self.upper_bound}"


class DepthFirstSearch(IntegratedAlgorithm):
    """Build a DFS call for a Cypher query.
    The Depth-First Search can be called in Memgraph with Cypher queries
    such as:
    MATCH (a {id: 723})-[* ..10 (r, n | r.x > 12 AND n.y < 3)]-() RETURN *;
    It is called inside the relationship clause, "*" naming the algorithm
    ("*" without "DFS" because it is defined like such in openCypher),
    "..10" specifying depth bounds, and "(r, n | <expression>)" is a filter
    lambda.
    """

    def __init__(
        self,
        lower_bound: int = None,
        upper_bound: int = None,
        condition: str = None,
    ) -> None:
        """
        Args:
            lower_bound: Lower bound for path depth.
            upper_bound: Upper bound for path depth.
            condition: Filter through nodes and relationships that pass this
            condition.
        """
        super().__init__()
        self.lower_bound = str(lower_bound) if lower_bound is not None else ""
        self.upper_bound = str(upper_bound) if upper_bound is not None else ""
        self.condition = condition

    def __str__(self) -> str:
        """get Cypher query string for this algorithm."""
        algo_str = DFS_EXPANSION

        bounds = self.to_cypher_bounds()
        if bounds != "":
            algo_str = f"{algo_str} {bounds}"

        filter_lambda = super().to_cypher_lambda(self.condition)
        if filter_lambda != "":
            algo_str = f"{algo_str} {filter_lambda}"

        return algo_str

    def to_cypher_bounds(self) -> str:
        """If bounds are specified, returns them in grammar-defined form."""
        if self.lower_bound == "" and self.upper_bound == "":
            return ""

        return f"{self.lower_bound}..{self.upper_bound}"


class WeightedShortestPath(IntegratedAlgorithm):
    """Build a Dijkstra shortest path call for a Cypher query.

    The weighted shortest path algorithm can be called in Memgraph with Cypher
    queries such as:
    " MATCH (a {id: 723})-[r *WSHORTEST 10 (r, n | r.weight) weight_sum
            (r, n | r.x > 12 AND r.y < 3)]-(b {id: 882}) RETURN * "
    It is called inside the relationship clause, "*WSHORTEST" naming the
    algorithm, "10" specifying search depth bounds, and "(r, n | <expression>)"
    is a filter lambda, used to filter which relationships and nodes to use.
    """

    def __init__(
        self,
        upper_bound: int = None,
        condition: str = None,
        total_weight_var: str = DEFAULT_TOTAL_WEIGHT,
        weight_property: str = DEFAULT_WEIGHT_PROPERTY,
    ) -> None:
        """
        Args:
            upper_bound: Upper bound for path depth.
            condition: Filter through nodes and relationships that pass this
            condition.
            total_weight_var: Variable defined as the sum of all weights on
            path being returned.
            weight_property: property being used as weight.
        """
        super().__init__()
        self.weight_property = weight_property if "." in weight_property else f"r.{weight_property}"
        self.total_weight_var = total_weight_var
        self.condition = condition
        self.upper_bound = "" if upper_bound is None else str(upper_bound)

    def __str__(self) -> str:
        algo_str = WSHORTEST_EXPANSION
        if self.upper_bound != "":
            algo_str = f"{algo_str} {self.upper_bound}"

        algo_str = f"{algo_str} {super().to_cypher_lambda(self.weight_property)} {self.total_weight_var}"

        filter_lambda = super().to_cypher_lambda(self.condition)
        if filter_lambda != "":
            algo_str = f"{algo_str} {filter_lambda}"

        return algo_str


class AllShortestPath(IntegratedAlgorithm):
    """Build a Dijkstra shortest path call for a Cypher query.

    The weighted shortest path algorithm can be called in Memgraph with Cypher
    queries such as:
    " MATCH (a {id: 723})-[r *ALLSHORTEST 10 (r, n | r.weight) total_weight
            (r, n | r.x > 12 AND r.y < 3)]-(b {id: 882}) RETURN * "
    It is called inside the relationship clause, "*ALLSHORTEST" naming the
    algorithm, "10" specifying search depth bounds, and "(r, n | <expression>)"
    is a filter lambda, used to filter which relationships and nodes to use.
    """

    def __init__(
        self,
        upper_bound: int = None,
        condition: str = None,
        total_weight_var: str = DEFAULT_TOTAL_WEIGHT,
        weight_property: str = DEFAULT_WEIGHT_PROPERTY,
    ) -> None:
        """
        Args:
            upper_bound: Upper bound for path depth.
            condition: Filter through nodes and relationships that pass this
            condition.
            total_weight_var: Variable defined as the sum of all weights on
            path being returned.
            weight_property: Property being used as weight.
        """
        super().__init__()
        self.weight_property = weight_property if "." in weight_property else f"r.{weight_property}"
        self.total_weight_var = total_weight_var
        self.condition = condition
        self.upper_bound = "" if upper_bound is None else str(upper_bound)

    def __str__(self) -> str:
        algo_str = ALLSHORTEST_EXPANSION
        if self.upper_bound != "":
            algo_str = f"{algo_str} {self.upper_bound}"

        algo_str = f"{algo_str} {super().to_cypher_lambda(self.weight_property)} {self.total_weight_var}"

        filter_lambda = super().to_cypher_lambda(self.condition)
        if filter_lambda != "":
            algo_str = f"{algo_str} {filter_lambda}"

        return algo_str
