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
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

from pydantic.v1 import BaseModel, Extra, Field, PrivateAttr  # noqa F401

from gqlalchemy.exceptions import (
    GQLAlchemyError,
    GQLAlchemySubclassNotFoundWarning,
    GQLAlchemyDatabaseMissingInFieldError,
    GQLAlchemyDatabaseMissingInNodeClassError,
)

# Suppress the warning GQLAlchemySubclassNotFoundWarning
IGNORE_SUBCLASSNOTFOUNDWARNING = False


class DatetimeKeywords(Enum):
    DURATION = "duration"
    LOCALTIME = "localTime"
    LOCALDATETIME = "localDateTime"
    DATE = "date"


datetimeKwMapping = {
    timedelta: DatetimeKeywords.DURATION.value,
    time: DatetimeKeywords.LOCALTIME.value,
    datetime: DatetimeKeywords.LOCALDATETIME.value,
    date: DatetimeKeywords.DATE.value,
}


def _format_timedelta(duration: timedelta) -> str:
    days = int(duration.total_seconds() // 86400)
    remainder_sec = duration.total_seconds() - days * 86400
    hours = int(remainder_sec // 3600)
    remainder_sec -= hours * 3600
    minutes = int(remainder_sec // 60)
    remainder_sec -= minutes * 60

    return f"P{days}DT{hours}H{minutes}M{remainder_sec}S"


class TriggerEventType:
    """An enum representing types of trigger events."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

    @classmethod
    def list(cls):
        return [cls.CREATE, cls.UPDATE, cls.DELETE]


class TriggerEventObject:
    """An enum representing types of trigger objects.

    NODE -> `()`
    RELATIONSHIP -> `-->`
    """

    NODE = "()"
    RELATIONSHIP = "-->"

    @classmethod
    def list(cls):
        return [cls.NODE, cls.RELATIONSHIP]


class TriggerExecutionPhase:
    """An enum representing types of trigger objects.

    Enum:
        BEFORE
        AFTER
    """

    BEFORE = "BEFORE"
    AFTER = "AFTER"


class FieldAttrsConstants:
    INDEX = "index"
    EXISTS = "exists"
    UNIQUE = "unique"

    @classmethod
    def list(cls):
        return [cls.INDEX, cls.EXISTS, cls.UNIQUE]


@dataclass(frozen=True, eq=True)
class Index(ABC):
    label: str
    property: Optional[str] = None

    def to_cypher(self) -> str:
        return f":{self.label}{f'({self.property})' if self.property else ''}"


@dataclass(frozen=True, eq=True)
class MemgraphIndex(Index):
    pass


@dataclass(frozen=True, eq=True)
class Neo4jIndex(Index):
    type: Optional[str] = None
    uniqueness: Optional[str] = None


@dataclass(frozen=True, eq=True)
class Constraint(ABC):
    label: str

    @abstractmethod
    def to_cypher(self) -> str:
        pass


@dataclass(frozen=True, eq=True)
class MemgraphConstraintUnique(Constraint):
    property: Union[str, Tuple]

    def to_cypher(self) -> str:
        properties_str = ""
        if isinstance(self.property, (tuple, set, list)):
            properties_str = ", ".join([f"n.{prop}" for prop in self.property])
        else:
            properties_str = f"n.{self.property}"
        return f"(n:{self.label}) ASSERT {properties_str} IS UNIQUE"


@dataclass(frozen=True, eq=True)
class MemgraphConstraintExists(Constraint):
    property: str

    def to_cypher(self) -> str:
        return f"(n:{self.label}) ASSERT EXISTS (n.{self.property})"


@dataclass(frozen=True, eq=True)
class Neo4jConstraintUnique(Constraint):
    property: Union[str, Tuple]

    def to_cypher(self) -> str:
        properties_str = ""
        if isinstance(self.property, (tuple, set, list)):
            properties_str = ", ".join([f"n.{prop}" for prop in self.property])
        else:
            properties_str = f"n.{self.property}"
        return f"(n:{self.label}) ASSERT {properties_str} IS UNIQUE"


@dataclass(frozen=True, eq=True)
class Neo4jConstraintExists(Constraint):
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


class MemgraphKafkaStream(MemgraphStream):
    """A class for creating and managing Kafka streams in Memgraph.

    Args:
        name: A string representing the stream name.
        topics: A list of strings representing the stream topics.
        transform: A string representing the name of the transformation procedure.
        consumer_group: A string representing the consumer group.
        name: A string representing the batch interval.
        name: A string representing the batch size.
        name: A string or list of strings representing bootstrap server addresses.
    """

    def __init__(
        self,
        name: str,
        topics: List[str],
        transform: str,
        consumer_group: str = None,
        batch_interval: str = None,
        batch_size: str = None,
        bootstrap_servers: Union[str, List[str]] = None,
    ):
        super().__init__(name, topics, transform)
        self.consumer_group = consumer_group
        self.batch_interval = batch_interval
        self.batch_size = batch_size
        self.bootstrap_servers = bootstrap_servers

    def to_cypher(self) -> str:
        """Converts Kafka stream to a Cypher clause."""
        topics = ",".join(self.topics)
        query = f"CREATE KAFKA STREAM {self.name} TOPICS {topics} TRANSFORM {self.transform}"
        if self.consumer_group is not None:
            query += f" CONSUMER_GROUP {self.consumer_group}"
        if self.batch_interval is not None:
            query += f" BATCH_INTERVAL {self.batch_interval}"
        if self.batch_size is not None:
            query += f" BATCH_SIZE {self.batch_size}"
        if self.bootstrap_servers is not None:
            if isinstance(self.bootstrap_servers, str):
                servers_field = f"'{self.bootstrap_servers}'"
            else:
                servers_field = str(self.bootstrap_servers)[1:-1]
            query += f" BOOTSTRAP_SERVERS {servers_field}"
        query += ";"
        return query


class MemgraphPulsarStream(MemgraphStream):
    """A class for creating and managing Pulsar streams in Memgraph.

    Args:
        name: A string representing the stream name.
        topics: A list of strings representing the stream topics.
        transform: A string representing the name of the transformation procedure.
        consumer_group: A string representing the consumer group.
        name: A string representing the batch interval.
        name: A string representing the batch size.
        name: A string or list of strings representing bootstrap server addresses.
    """

    def __init__(
        self,
        name: str,
        topics: List[str],
        transform: str,
        batch_interval: str = None,
        batch_size: str = None,
        service_url: str = None,
    ):
        super().__init__(name, topics, transform)
        self.batch_interval = batch_interval
        self.batch_size = batch_size
        self.service_url = service_url

    def to_cypher(self) -> str:
        """Converts Pulsar stream to a Cypher clause."""
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
    execution_phase: TriggerExecutionPhase
    statement: str
    event_type: Optional[TriggerEventType] = None
    event_object: Optional[TriggerEventObject] = None

    def to_cypher(self) -> str:
        """Converts a Trigger to a cypher clause."""
        query = f"CREATE TRIGGER {self.name} "
        if self.event_type in TriggerEventType.list():
            query += f"ON " + (
                f"{self.event_object} {self.event_type} "
                if self.event_object in TriggerEventObject.list()
                else f"{self.event_type} "
            )
        query += f"{self.execution_phase} COMMIT EXECUTE "
        query += f"{self.statement};"
        return query


class GraphObject(BaseModel):
    _subtypes_: Dict = dict()

    class Config:
        extra = Extra.allow

    def __init_subclass__(cls, type=None, label=None, labels=None, index=None, db=None):
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
            if not IGNORE_SUBCLASSNOTFOUNDWARNING:
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
        self, value: Union[None, bool, int, float, str, list, dict, datetime, timedelta, date, time]
    ) -> str:
        value_type = type(value)

        if value is None:
            "Null"
        elif value_type == bool:
            return repr(value)
        elif value_type == int:
            return repr(value)
        elif value_type == float:
            return repr(value)
        elif isinstance(value, str):
            return repr(value) if value.isprintable() else rf"'{value}'"
        elif isinstance(value, list):
            return "[" + ", ".join(self.escape_value(val) for val in value) + "]"
        elif value_type == dict:
            return "{" + ", ".join(f"{key}: {self.escape_value(val)}" for key, val in value.items()) + "}"
        if isinstance(value, (timedelta, time, datetime, date)):
            return f"{datetimeKwMapping[value_type]}('{_format_timedelta(value) if isinstance(value, timedelta) else value.isoformat()}')"
        else:
            raise GQLAlchemyError(
                f"Unsupported value data type: {type(value)}."
                + " Memgraph supports the following data types:"
                + " None, bool, int, float, str, list, dict, datetime."
            )

    def _get_cypher_field_assignment_block(self, variable_name: str, operator: str) -> str:
        """Creates a cypher field assignment block joined using the `operator`
        argument.
        Example:
            self = {"name": "John", "age": 34}
            variable_name = "user"
            operator = " AND "

            returns:
                "user.name = 'John' AND user.age = 34"
        """
        cypher_fields = []
        for field in self.__fields__:
            value = getattr(self, field)
            if value is not None:
                cypher_fields.append(f"{variable_name}.{field} = {self.escape_value(value)}")

        return " " + operator.join(cypher_fields) + " "

    def _get_cypher_fields_or_block(self, variable_name: str) -> str:
        """Returns a cypher field assignment block separated by an OR
        statement.
        """
        return self._get_cypher_field_assignment_block(variable_name, " OR ")

    def _get_cypher_fields_and_block(self, variable_name: str) -> str:
        """Returns a cypher field assignment block separated by an AND
        statement.
        """
        return self._get_cypher_field_assignment_block(variable_name, " AND ")

    def _get_cypher_fields_xor_block(self, variable_name: str) -> str:
        """Returns a cypher field assignment block separated by an XOR
        statement.
        """
        return self._get_cypher_field_assignment_block(variable_name, " XOR ")

    # TODO: add NOT

    def _get_cypher_set_properties(self, variable_name: str) -> str:
        """Returns a cypher set properties block."""
        cypher_set_properties = []
        for field in self.__fields__:
            attributes = self.__fields__[field].field_info.extra
            value = getattr(self, field)
            if value is not None and not attributes.get("on_disk", False):
                cypher_set_properties.append(f" SET {variable_name}.{field} = {self.escape_value(value)}")

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
        return {k: v for k, v in dict(self).items() if not k.startswith("_") and k != "labels"}

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

        def field_in_superclass(field, constraint):
            nonlocal bases
            for base in bases:
                if field in base.__fields__:
                    attrs = base.__fields__[field].field_info.extra
                    if constraint in attrs:
                        return base

            return None

        def get_base_labels() -> Set[str]:
            base_labels = set()
            nonlocal bases
            for base in bases:
                if hasattr(base, "labels"):
                    base_labels = base_labels.union(base.labels)

            return base_labels

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        cls.index = kwargs.get("index")
        cls.label = kwargs.get("label", name)
        if name != "Node":
            cls.labels = get_base_labels().union({cls.label}, kwargs.get("labels", set()))

        db = kwargs.get("db")
        if cls.index is True:
            if db is None:
                raise GQLAlchemyDatabaseMissingInNodeClassError(cls=cls)

            index = MemgraphIndex(cls.label)
            db.create_index(index)

        for field in cls.__fields__:
            attrs = cls.__fields__[field].field_info.extra
            field_type = cls.__fields__[field].type_.__name__
            label = attrs.get("label", cls.label)
            skip_constraints = False

            if db is None:
                db = attrs.get("db")

            for constraint in FieldAttrsConstants.list():
                if constraint in attrs and db is None:
                    base = field_in_superclass(field, constraint)
                    if base is not None:
                        cls.__fields__[field].field_info.extra = base.__fields__[field].field_info.extra
                        skip_constraints = True
                        break

                    raise GQLAlchemyDatabaseMissingInFieldError(
                        constraint=constraint,
                        field=field,
                        field_type=field_type,
                    )

            if skip_constraints:
                continue

            if FieldAttrsConstants.INDEX in attrs and attrs[FieldAttrsConstants.INDEX] is True:
                index = MemgraphIndex(label, field)
                db.create_index(index)

            if FieldAttrsConstants.EXISTS in attrs and attrs[FieldAttrsConstants.EXISTS] is True:
                constraint = MemgraphConstraintExists(label, field)
                db.create_constraint(constraint)

            if FieldAttrsConstants.UNIQUE in attrs and attrs[FieldAttrsConstants.UNIQUE] is True:
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
        """Get's a cypher assignment block using the unique fields."""
        cypher_unique_fields = []
        for field in self.__fields__:
            attrs = self.__fields__[field].field_info.extra
            if "unique" in attrs:
                value = getattr(self, field)
                if value is not None:
                    cypher_unique_fields.append(f"{variable_name}.{field} = {self.escape_value(value)}")

        return " " + " OR ".join(cypher_unique_fields) + " "

    def has_unique_fields(self) -> bool:
        """Returns True if the Node has any unique fields."""
        for field in self.__fields__:
            if "unique" in self.__fields__[field].field_info.extra:
                if getattr(self, field) is not None:
                    return True
        return False

    @property
    def _label(self) -> str:
        return ":".join(sorted(self._labels))

    def save(self, db: "Database") -> "Node":  # noqa F821
        """Saves node to Memgraph.
        If the node._id is not None it fetches the node with the same id from
        Memgraph and updates it's fields.
        If the node has unique fields it fetches the nodes with the same unique
        fields from Memgraph and updates it's fields.
        Otherwise it creates a new node with the same properties.
        Null properties are ignored.
        """
        node = db.save_node(self)
        for field in self.__fields__:
            setattr(self, field, getattr(node, field))
        self._id = node._id
        return self

    def load(self, db: "Database") -> "Node":  # noqa F821
        """Loads a node from Memgraph.
        If the node._id is not None it fetches the node from Memgraph with that
        internal id.
        If the node has unique fields it fetches the node from Memgraph with
        those unique fields set.
        Otherwise it tries to find any node in Memgraph that has all properties
        set to exactly the same values.
        If no node is found or no properties are set it raises a GQLAlchemyError.
        """
        node = db.load_node(self)
        for field in self.__fields__:
            setattr(self, field, getattr(node, field))
        self._id = node._id
        return self

    def get_or_create(self, db: "Database") -> Tuple["Node", bool]:  # noqa F821
        """Return the node and a flag for whether it was created in the database.

        Args:
            db: The database instance to operate on.

        Returns:
            A tuple with the first component being the created graph node,
            and the second being a boolean that is True if the node
            was created in the database, and False if it was loaded instead.
        """
        try:
            return self.load(db=db), False
        except GQLAlchemyError:
            return self.save(db=db), True


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

    def save(self, db: "Database") -> "Relationship":  # noqa F821
        """Saves a relationship to Memgraph.
        If relationship._id is not None it finds the relationship in Memgraph
        and updates it's properties with the values in `relationship`.
        If relationship._id is None, it creates a new relationship.
        If you want to set a relationship._id instead of creating a new
        relationship, use `load_relationship` first.
        """
        relationship = db.save_relationship(self)
        for field in self.__fields__:
            setattr(self, field, getattr(relationship, field))
        self._id = relationship._id
        return self

    def load(self, db: "Database") -> "Relationship":  # noqa F821
        """Returns a relationship loaded from Memgraph.
        If the relationship._id is not None it fetches the relationship from
        Memgraph that has the same internal id.
        Otherwise it returns the relationship whose relationship._start_node_id
        and relationship._end_node_id and all relationship properties that
        are not None match the relationship in Memgraph.
        If there is no relationship like that in Memgraph, or if there are
        multiple relationships like that in Memgraph, throws GQLAlchemyError.
        """
        relationship = db.load_relationship(self)
        for field in self.__fields__:
            setattr(self, field, getattr(relationship, field))
        self._id = relationship._id
        return self

    def get_or_create(self, db: "Database") -> Tuple["Relationship", bool]:  # noqa F821
        """Return the relationship and a flag for whether it was created in the database.

        Args:
            db: The database instance to operate on.

        Returns:
            A tuple with the first component being the created graph relationship,
            and the second being a boolean that is True if the relationship
            was created in the database, and False if it was loaded instead.
        """
        try:
            return self.load(db=db), False
        except GQLAlchemyError:
            return self.save(db=db), True


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
