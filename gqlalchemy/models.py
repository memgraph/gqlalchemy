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

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Union
from pydantic import BaseModel, PrivateAttr

from .utilities import GQLAlchemyWarning


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
        """Stores the subclass by type if type is specified, or by class name
        when instantiating a subclass.
        """
        cls._subtypes_[type or cls.__name__] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        """Converts the GraphObject class into the appropriate subclass.
        This is used when deserialising a json representation of the class,
        or the object returned from the GraphDatabase.
        """
        data_type = data.get("type")

        sub = cls if data_type is None else cls._subtypes_.get(data_type)

        if sub is None:
            warnings.warn(  # GQLAlchemy failed to find a subclass. #  )
                f"GraphObject subclass '{data_type}' not found. "
                f"'{cls.__name__}' will be used until you create a subclass.",
                GQLAlchemyWarning,
            )
            sub = cls

        return sub(**data)

    @classmethod
    def parse_obj(cls, obj):
        """Used to convert a dictionary object into the appropriate
        GraphObject.
        """
        return cls._convert_to_real_type_(obj)

    def __str__(self) -> str:
        return "<GraphObject>"

    def __repr__(self) -> str:
        return str(self)


class UniqueGraphObject(GraphObject):
    _id: Optional[Any] = PrivateAttr()
    _properties: Optional[Dict[str, Any]] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._id = data.get("_id")
        self._properties = data.get("_properties")

    def __str__(self) -> str:
        return f"<GraphObject id={self._id} properties={self._properties}>"

    def __repr__(self) -> str:
        return str(self)


class Node(UniqueGraphObject):
    _node_id: Optional[Any] = PrivateAttr()
    _node_labels: Optional[Set[str]] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._node_id = data.get("_node_id")
        self._node_labels = data.get("_node_labels")

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" id={self._id}",
                f" labels={self._node_labels}",
                f" properties={self._properties}",
                ">",
            )
        )


class Relationship(UniqueGraphObject):
    _relationship_id: Any = PrivateAttr()
    _relationship_type: str = PrivateAttr()
    _start_node_id: int = PrivateAttr()
    _end_node_id: int = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._relationship_id = data.get("_relationship_id")
        self._relationship_type = data.get("_relationship_type")
        self._start_node_id = data.get("_start_node_id")
        self._end_node_id = data.get("_end_node_id")

    @property
    def _nodes(self) -> Tuple[int, int]:
        return (self._start_node_id, self._end_node_id)

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" id={self._id}",
                f" nodes={self._nodes}",
                f" relationship_type={self._relationship_type}",
                f" properties={self._properties}",
                ">",
            )
        )


class Path(GraphObject):
    _nodes: Iterable[Node] = PrivateAttr()
    _relationships: Iterable[Relationship] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._nodes = data.get("_nodes")
        self._relationships = data.get("_relationships")

    def get_nodes(self) -> Iterable[Node]:
        return self._nodes

    def get_relationships(self) -> Iterable[Relationship]:
        return self._relationships

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" nodes={self._nodes}",
                f" relationships={self._relationships}" ">",
            )
        )
