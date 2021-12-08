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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Union

from pydantic import BaseModel


@dataclass(frozen=True, eq=True)
class MemgraphIndex:
    label: str
    property: Optional[str] = None

    def to_cypher(self) -> str:
        property_cypher = f"({self.property})" if self.property else ""
        return f":{self.label}{property_cypher}"


@dataclass(frozen=True, eq=True)
class MemgraphConstraint(ABC):
    label: str

    @abstractmethod
    def to_cypher(self) -> str:
        pass


@dataclass(frozen=True, eq=True)
class MemgraphConstraintUnique(MemgraphConstraint):
    property: Union[str, Tuple]

    def to_cypher(self) -> str:
        properties_str = ""
        if isinstance(self.property, (tuple, set, list)):
            properties_str = ", ".join([f"n.{prop}" for prop in self.property])
        else:
            properties_str = f"n.{self.property}"
        return f"(n:{self.label}) ASSERT {properties_str} IS UNIQUE"


@dataclass(frozen=True, eq=True)
class MemgraphConstraintExists(MemgraphConstraint):
    property: str

    def to_cypher(self) -> str:
        return f"(n:{self.label}) ASSERT EXISTS (n.{self.property})"


class GraphObject(BaseModel):
    _subtypes_ = dict()

    def __init_subclass__(cls, type=None):
        cls._subtypes_[type or cls.__name__.lower()] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        data_type = data.get("type")

        if data_type is None:
            raise ValueError("Unsupported type.")

        sub = cls._subtypes_.get(data_type)

        if sub is None:
            raise TypeError(f"Unsupport sub-type: {data_type}")

        return sub(**data)

    @classmethod
    def parse_obj(cls, obj):
        return cls._convert_to_real_type_(obj)

    def __str__(self) -> str:
        return "<GraphObject>"

    def __repr__(self) -> str:
        return str(self)


class UniqueGraphObject(GraphObject):
    id: Optional[Any]
    properties: Optional[Dict[str, Any]]

    def __str__(self) -> str:
        return f"<GraphObject id={self.id} properties={self.properties}>"

    def __repr__(self) -> str:
        return str(self)


class Node(UniqueGraphObject, BaseModel):
    node_id: Optional[Any]
    labels: Optional[Set[str]]
    properties: Optional[Dict[str, Any]]

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" id={self.id}",
                f" labels={self.labels}",
                f" properties={self.properties}",
                ">",
            )
        )


class Relationship(UniqueGraphObject):
    def __init__(
        self,
        rel_id: Any,
        rel_type: str,
        start_node: int,
        end_node: int,
        properties: Dict[str, Any] = None,
    ):
        super().__init__(rel_id, properties)
        self._type = rel_type
        self._start_node = start_node
        self._end_node = end_node

    @property
    def type(self) -> str:
        return self._type

    @property
    def end_node(self) -> int:
        return self._end_node

    @property
    def start_node(self) -> int:
        return self._start_node

    @property
    def nodes(self) -> Tuple[int, int]:
        return (self.start_node, self.end_node)

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" id={self.id}",
                f" nodes={self.nodes}",
                f" type={self.type}",
                f" properties={self.properties}",
                ">",
            )
        )


class Path(GraphObject):
    def __init__(self, nodes: Iterable[Node], relationships: Iterable[Relationship]):
        self._nodes = nodes
        self._relationships = relationships

    @property
    def nodes(self) -> Iterable[Node]:
        return self._nodes

    @property
    def relationships(self) -> Iterable[Relationship]:
        return self._relationships

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" nodes={self.nodes}",
                f" relationships={self.relationships}" ">",
            )
        )
