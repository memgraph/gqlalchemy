# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
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
import datetime

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Iterable, Optional, Set, Tuple, Union
from pydantic import BaseModel, PrivateAttr, Extra

from .exceptions import (
    GQLAlchemyError,
    GQLAlchemySubclassNotFoundWarning,
    GQLAlchemyDatabaseMissingInFieldError,
)


class TriggerEventType:
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class TriggerEventObject:
    ALL = ""
    NODE = "()"
    RELATIONSHIP = "-->"


class TriggerExecutionPhase:
    BEFORE = "BEFORE"
    AFTER = "AFTER"


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


@dataclass(frozen=True, eq=True)
class MemgraphStream(ABC):
    name: str
    topics: List[str]
    transform: str

    @abstractmethod
    def to_cypher(self) -> str:
        pass


@dataclass(frozen=True, eq=True)
class MemgraphKafkaStream(MemgraphStream):
    consumer_group: str = None
    batch_interval: str = None
    batch_size: str = None
    bootstrap_servers: str = None

    def to_cypher(self) -> str:
        topics = ",".join(self.topics)
        query = f"CREATE KAFKA STREAM {self.name} TOPICS {topics} TRANSFORM {self.transform}"
        if self.consumer_group is not None:
            query += f" CONSUMER_GROUP {self.consumer_group}"
        if self.batch_interval is not None:
            query += f" BATCH_INTERVAL {self.batch_interval}"
        if self.batch_size is not None:
            query += f" BATCH_SIZE {self.batch_size}"
        if self.bootstrap_servers is not None:
            query += f" BOOTSTRAP_SERVERS {self.bootstrap_servers}"
        query += ";"
        return query


@dataclass(frozen=True, eq=True)
class MemgraphPulsarStream(MemgraphStream):
    batch_interval: str = None
    batch_size: str = None
    service_url: str = None

    def to_cypher(self) -> str:
        topics = ",".join(self.topics)
        query = f"CREATE PULSAR STREAM {self.name} TOPICS {topics} TRANSFORM {self.transform}"
        if self.batch_interval is not None:
            query += f" BATCH_INTERVAL {self.batch_interval}"
        if self.batch_size is not None:
            query += f" BATCH_SIZE {self.batch_size}"
        if self.service_url is not None:
            query += f" SERVICE_URL {self.service_url}"
        query += ";"
        return query


@dataclass(frozen=True, eq=True)
class MemgraphTrigger:
    name: str
    event_type: TriggerEventType
    event_object: TriggerEventObject
    execution_phase: TriggerExecutionPhase
    statement: str

    def to_cypher(self) -> str:
        query = f"CREATE TRIGGER {self.name} "
        # when self.event_object is TriggerEventObject.ALL there is a double space
        query += f"ON {self.event_object} {self.event_type} "
        query += f"{self.execution_phase} COMMIT EXECUTE "
        query += f"{self.statement};"
        return query


class GraphObject(BaseModel):
    _subtypes_ = dict()

    class Config:
        extra = Extra.allow

    def __init_subclass__(cls, type=None, label=None, labels=None):
        """Stores the subclass by type if type is specified, or by class name
        when instantiating a subclass.
        """
        if type is not None:  # Relationship
            cls._subtypes_[type] = cls
        elif label is not None:  # Node
            cls._subtypes_[label] = cls
        else:
            cls._subtypes_[cls.__name__] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        """Converts the GraphObject class into the appropriate subclass.
        This is used when deserialising a json representation of the class,
        or the object returned from the GraphDatabase.
        """
        sub = None
        if "_type" in data:  # Relationship
            sub = cls._subtypes_.get(data.get("_type"))

        if "_labels" in data:  # Node
            # Find class that has the most super classes
            labels = data["_labels"]
            classes = [cls._subtypes_[label] for label in labels if label in cls._subtypes_]
            counter = defaultdict(int)
            for class1 in classes:
                counter[class1] += sum(issubclass(class1, class2) for class2 in classes)
            if counter:
                sub = max(counter, key=counter.get)

        if sub is None:
            types = data.get("_type", data.get("_labels"))
            warnings.warn(GQLAlchemySubclassNotFoundWarning(types, cls))
            sub = cls

        return sub(**data)

    @classmethod
    def parse_obj(cls, obj):
        """Used to convert a dictionary object into the appropriate
        GraphObject.
        """
        return cls._convert_to_real_type_(obj)

    def escape_value(
        self, value: Union[None, bool, int, float, str, list, dict, datetime.datetime], in_list_or_dict=False
    ) -> str:
        if value is None:
            "Null"
        elif isinstance(value, bool):
            return repr(value)
        elif isinstance(value, int):
            return repr(value)
        elif isinstance(value, float):
            return repr(value)
        elif isinstance(value, str):
            return repr(value)
        elif isinstance(value, list):
            return "[" + ", ".join(self.escape_value(val, True) for val in value) + "]"
        elif isinstance(value, dict):
            return "{" + ", ".join(f"{val}: {self.escape_value(val, True)}" for key, val in value.items()) + "}"
        elif isinstance(value, datetime.datetime):
            return value.isoformat()
        else:
            raise GQLAlchemyError(
                f"Unsupported value data type: {type(value)}."
                + " Memgraph supports the following data types:"
                + " None, bool, int, float, str, list, dict, datetime.datetime."
            )

    def _get_cypher_field_assignment_block(self, variable_name: str, operator: str) -> str:
        cypher_fields = []
        for field in self.__fields__:
            value = getattr(self, field)
            if value is not None:
                cypher_fields.append(f"{variable_name}.{field} = {self.escape_value(value)}")

        return " " + operator.join(cypher_fields) + " "

    def _get_cypher_fields_or_block(self, variable_name: str) -> str:
        return self._get_cypher_field_assignment_block(variable_name, " OR ")

    def _get_cypher_fields_and_block(self, variable_name: str) -> str:
        return self._get_cypher_field_assignment_block(variable_name, " AND ")

    def _get_cypher_set_properties(self, variable_name: str) -> str:
        cypher_set_properties = []
        for field in self.__fields__:
            attributes = self.__fields__[field].field_info.extra
            value = getattr(self, field)
            if value is not None and not attributes.get("on_disk", False):
                cypher_set_properties.append(f" SET {variable_name}.{field} = {repr(value)}")

        return " " + " ".join(cypher_set_properties) + " "

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


class NodeMetaclass(BaseModel.__class__):
    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa C901
        """This creates the class `Node`. It also creates all subclasses
        of `Node`. Whenever a class is defined as a subclass of `Node`,
        `MyMeta.__new__` is called.
        """
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        cls.label = kwargs.get("label", name)
        if name == "Node":
            pass
        elif "labels" in kwargs:  # overrides superclass labels
            cls.labels = kwargs["labels"]
        elif hasattr(cls, "labels"):
            cls.labels = cls.labels | {cls.label}
        else:
            cls.labels = {cls.label}

        for field in cls.__fields__:
            attrs = cls.__fields__[field].field_info.extra
            field_type = cls.__fields__[field].type_.__name__

            label = attrs.get("label", cls.label)
            db = attrs.get("db", None)
            for constraint in ["index", "unique", "exists"]:
                if constraint in attrs and db is None:
                    raise GQLAlchemyDatabaseMissingInFieldError(
                        constraint=constraint,
                        field=field,
                        field_type=field_type,
                    )

            if "index" in attrs:
                index = MemgraphIndex(label, field)
                db.create_index(index)

            if "exists" in attrs:
                constraint = MemgraphConstraintExists(label, field)
                db.create_constraint(constraint)

            if "unique" in attrs:
                constraint = MemgraphConstraintUnique(label, field)
                db.create_constraint(constraint)

            if attrs and "db" in attrs:
                del attrs["db"]
        return cls


class Node(UniqueGraphObject, metaclass=NodeMetaclass):
    _labels: Set[str] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._labels = data.get("_labels", getattr(type(self), "labels", {"Node"}))

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" id={self._id}",
                f" labels={self._labels}",
                f" properties={self._properties}",
                ">",
            )
        )

    def _get_cypher_unique_fields_or_block(self, variable_name: str) -> str:
        cypher_unique_fields = []
        for field in self.__fields__:
            attrs = self.__fields__[field].field_info.extra
            if "unique" in attrs:
                value = getattr(self, field)
                if value is not None:
                    cypher_unique_fields.append(f"{variable_name}.{field} = {repr(value)}")

        return " " + " OR ".join(cypher_unique_fields) + " "

    def has_unique_fields(self) -> bool:
        for field in self.__fields__:
            if "unique" in self.__fields__[field].field_info.extra:
                if getattr(self, field) is not None:
                    return True
        return False

    @property
    def _label(self) -> str:
        return ":".join(sorted(self._labels))

    def save(self, db: "Memgraph") -> "Node":  # noqa F821
        node = db.save_node(self)
        for field in self.__fields__:
            setattr(self, field, getattr(node, field))
        self._id = node._id
        return self

    def load(self, db: "Memgraph") -> "Node":  # noqa F821
        node = db.load_node(self)
        for field in self.__fields__:
            setattr(self, field, getattr(node, field))
        self._id = node._id
        return self


class RelationshipMetaclass(BaseModel.__class__):
    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa C901
        """This creates the class `Relationship`. It also creates all
        subclasses of `Relationship`. Whenever a class is defined as a
        subclass of `Relationship`, `self.__new__` is called.
        """
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if name != "Relationship":
            cls.type = kwargs.get("type", name)

        return cls


class Relationship(UniqueGraphObject, metaclass=RelationshipMetaclass):
    _end_node_id: int = PrivateAttr()
    _start_node_id: int = PrivateAttr()
    _type: str = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._start_node_id = data.get("_start_node_id")
        self._end_node_id = data.get("_end_node_id")
        self._type = data.get("_type", getattr(type(self), "type", "Relationship"))

    @property
    def _nodes(self) -> Tuple[int, int]:
        return (self._start_node_id, self._end_node_id)

    def __str__(self) -> str:
        return "".join(
            (
                f"<{type(self).__name__}",
                f" id={self._id}",
                f" start_node_id={self._start_node_id}",
                f" end_node_id={self._end_node_id}",
                f" nodes={self._nodes}",
                f" type={self._type}",
                f" properties={self._properties}",
                ">",
            )
        )

    def save(self, db: "Memgraph") -> "Relationship":  # noqa F821
        relationship = db.save_relationship(self)
        for field in self.__fields__:
            setattr(self, field, getattr(relationship, field))
        self._id = relationship._id
        return self

    def load(self, db: "Memgraph") -> "Relationship":  # noqa F821
        relationship = db.load_relationship(self)
        for field in self.__fields__:
            setattr(self, field, getattr(relationship, field))
        self._id = relationship._id
        return self


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
