# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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
from pydantic import BaseModel, PrivateAttr, Extra

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

    class Config:
        extra = Extra.allow

    def __init_subclass__(cls, _type=None):
        """Stores the subclass by type if type is specified, or by class name
        when instantiating a subclass.
        """
        cls._subtypes_[_type or cls.__name__] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        """Converts the GraphObject class into the appropriate subclass.
        This is used when deserialising a json representation of the class,
        or the object returned from the GraphDatabase.
        """
        data_type = data.get("_type")

        sub = cls if data_type is None else cls._subtypes_.get(data_type)

        if sub is None:
            warnings.warn(  # GQLAlchemy failed to find a subclass. #  )
                f"GraphObject subclass '{data_type}' not found. "
                f"'{cls.__name__}' will be used until you create a subclass.",
                GQLAlchemyWarning,
            )
            sub = cls
            data_type = cls.__name__

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
        self._type = data.get("_type")

    @property
    def _properties(self) -> Dict[str, Any]:
        return {k: v for k, v in dict(self).items() if not k.startswith("_")}

    def __str__(self) -> str:
        return f"<GraphObject id={self._id} properties={self._properties}>"

    def __repr__(self) -> str:
        return str(self)


class MyMeta(BaseModel.__class__):
    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa C901
        """This creates the class `Node`. It also creates all subclasses
        of `Node`. Whenever a class is defined as a subclass of `Node`,
        `MyMeta.__new__` is called.
        """
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        # TODO create a discussion about accessing labels through the class definition instead of through the object. E.g. `Person.labels` instead of `person = Person("Marko"); person._node_labels`.
        cls._type = kwargs.get("_type", name)
        cls._node_labels = kwargs.get("_node_labels", set(cls._type.split(":")))
        labels = ":".join(cls._node_labels)
        # TODO check if *_type* or *_node_labels* is in fields
        for field in cls.__fields__:
            attrs = cls.__fields__[field].field_info.extra
            field_type = cls.__fields__[field].type_.__name__
            db = None
            if "db" in attrs:
                db = attrs["db"]

            if "index" in attrs:
                if db is None:
                    raise ValueError(
                        "Can't have an index on a property without providing"
                        " the database `db` object.\n"
                        "Define your property as:\n"
                        f" {field}: {field_type} = Field(index=True, db=Memgraph())"
                    )
                index = MemgraphIndex(labels, field)
                db.create_index(index)

            if "exists" in attrs:
                if db is None:
                    raise ValueError(
                        "Can't have an index on a property without providing"
                        " the database `db` object.\n"
                        "Define your property as:\n"
                        f" {field}: type = Field(exists=True, db=Memgraph())"
                    )
                constraint = MemgraphConstraintExists(labels, field)
                db.create_constraint(constraint)

            if "unique" in attrs:
                if db is None:
                    raise ValueError(
                        "Can't have an index on a property without providing"
                        " the database `db` object.\n"
                        "Define your property as:\n"
                        f" {field}: type = Field(unique=True, db=Memgraph())"
                    )
                constraint = MemgraphConstraintUnique(labels, field)
                db.create_constraint(constraint)

            # if "on_disk" in attrs:
            # if "use_in_db" in attrs:

        return cls


class Node(UniqueGraphObject, metaclass=MyMeta):
    _node_labels: Optional[Set[str]] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._type = data.get("_type", type(self).__name__)
        self._node_labels = data.get("_node_labels", set(self._type.split(":")))

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
    _relationship_type: str = PrivateAttr()
    _start_node_id: int = PrivateAttr()
    _end_node_id: int = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
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

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" nodes={self._nodes}",
                f" relationships={self._relationships}" ">",
            )
        )
