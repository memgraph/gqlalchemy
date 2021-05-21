import string
from typing import Any, Dict, Iterator, List, Optional, Union

from .memgraph import Memgraph
from memgraph.utilities import to_cypher_labels, to_cypher_properties, to_cypher_value

memgraph = Memgraph()


class MatchTypes:
    NODE = "node"
    EDGE = "edge"
    MATCH = "match"
    WHERE = "where"
    AND_WHERE = "and_where"
    OR_WHERE = "or_where"


class VariableDuplicatedMemgraph(Exception):
    def __init__(self, variable: Any):
        message = f"Variable {variable} has been mentioned more than once!"
        super().__init__(message)


class NumberOfVariablesMemgraph(Exception):
    def __init__(self):
        self._message = "The number of used variables has been exceeded, the number of variables is limited to 27!"
        super().__init__(self._message)


class Match:
    def __init__(self):
        self._query = []
        self._variables = set()

    def match(self, optional: bool = False) -> "Match":
        self._query.append({"optional": optional, "type": MatchTypes.MATCH})

        return self

    def node(
        self, labels: Union[str, Union[List[str], None]] = "", variable: Optional[str] = None, **kwargs
    ) -> "Match":
        labels_str = to_cypher_labels(labels)
        properties_str = to_cypher_properties(kwargs)

        self._query.append(
            {"variable": variable, "labels_str": labels_str, "properties_str": properties_str, "type": MatchTypes.NODE}
        )
        return self

    def to(
        self, edge_label: Optional[str] = "", directed: Optional[bool] = True, variable: Optional[str] = None, **kwargs
    ) -> "Match":
        labels_str = to_cypher_labels(edge_label)
        properties_str = to_cypher_properties(kwargs)

        self._query.append(
            {
                "variable": variable,
                "labels_str": labels_str,
                "properties_str": properties_str,
                "directed": directed,
                "type": MatchTypes.EDGE,
            }
        )

        return self

    def where(self, property: str, operator: str, value: Any) -> "Match":
        value_cypher = to_cypher_value(value)
        self._query.append({"query": " ".join([property, operator, value_cypher]), "type": MatchTypes.WHERE})
        return self

    def and_where(self, property: str, operator: str, value: Any) -> "Match":
        value_cypher = to_cypher_value(value)
        self._query.append({"query": " ".join([property, operator, value_cypher]), "type": MatchTypes.AND_WHERE})
        return self

    def or_where(self, property: str, operator: str, value: Any) -> "Match":
        value_cypher = to_cypher_value(value)
        self._query.append({"query": " ".join([property, operator, value_cypher]), "type": MatchTypes.OR_WHERE})
        return self

    def get_single(self, retrive: str) -> Any:
        query = self._construct_query()

        query += f" RETURN {retrive}"
        result = next(memgraph.execute_and_fetch(query), None)

        if result:
            return result[retrive]
        return result

    def execute(self, retrive: Optional[Union[List[str], str]] = None) -> Iterator[Dict[str, Any]]:
        query = self._construct_query()
        if not retrive:
            retrive_query = ",".join(self._variables)
        else:
            retrive_query = "*"
        query += f" RETURN {retrive_query}"

        return memgraph.execute_and_fetch(query)

    def _construct_query(self) -> str:
        query = ["MATCH "]
        self._assign_variables()
        for partial_query in self._query:
            if partial_query["type"] == MatchTypes.NODE:
                query.append(
                    f"({partial_query['variable']}{partial_query['labels_str']}{partial_query['properties_str']})"
                )
            elif partial_query["type"] == MatchTypes.EDGE:
                relationship_query = (
                    f"{partial_query['variable']}{partial_query['labels_str']}{partial_query['properties_str']}"
                )
                if partial_query["directed"]:
                    query.append(f"-[{relationship_query}]->")
                else:
                    query.append(f"-[{relationship_query}]-")
            elif partial_query["type"] == "match":
                if partial_query["optional"]:
                    query.append("\n OPTIONAL MATCH ")
                else:
                    query.append("\n MATCH ")
            elif partial_query["type"] == MatchTypes.WHERE:
                query.append(f"\n WHERE {partial_query['query']} ")
            elif partial_query["type"] == MatchTypes.AND_WHERE:
                query.append(f"\n AND {partial_query['query']} ")
            elif partial_query["type"] == MatchTypes.OR_WHERE:
                query.append(f"\n OR {partial_query['query']} ")
        return "".join(query)

    def _assign_variables(self) -> None:
        for partial_query in self._query:
            if self._should_partial_query_contain_variable(partial_query) and partial_query["variable"]:
                if partial_query["variable"] not in self._variables:
                    self._variables.add(partial_query["variable"])

        for partial_query in self._query:
            if self._should_partial_query_contain_variable(partial_query) and not partial_query["variable"]:
                variable = self._get_unassigned_letter()
                self._variables.add(variable)
                partial_query["variable"] = variable

    def _should_partial_query_contain_variable(self, query: Dict[str, Any]) -> bool:
        return query["type"] == MatchTypes.NODE or query["type"] == MatchTypes.EDGE

    def _get_unassigned_letter(self) -> str:
        for letter in string.ascii_lowercase:
            if letter not in self._variables:
                return letter
        raise NumberOfVariablesMemgraph()
