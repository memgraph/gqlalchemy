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
import time

DATABASE_MISSING_IN_FIELD_ERROR_MESSAGE = """
Can't have an index on a property without providing the database `db` object.
Define your property as:
  {field}: {field_type} = Field({constraint}=True, db=Memgraph())
"""

DATABASE_MISSING_IN_NODE_CLASS_ERROR_MESSAGE = """
Can't have an index on a label without providing the database `db` object.
Define your class as:
  {cls.__name__}(Node, index=True, db=Memgraph())
"""

SUBCLASS_NOT_FOUND_WARNING = """
GraphObject subclass(es) '{types}' not found.
'{cls.__name__}' will be used until you create a subclass.
"""

ON_DISK_PROPERTY_DATABASE_NOT_DEFINED_ERROR = """
Error: Saving a node with an on_disk property without specifying an on disk database.

Add an on_disk_db like this:

from gqlalchemy import Memgraph, SQLitePropertyDatabase

db = Memgraph()
SQLitePropertyDatabase("path-to-sqlite-db", db)
"""

MISSING_OPTIONAL_DEPENDENCY = """
No module named '{dependency_name}'
"""

MISSING_ORDER = """
The second argument of the tuple must be order: ASC, ASCENDING, DESC or DESCENDING.
"""

ORDER_BY_TYPE_ERROR = """
TypeError: The argument provided is of wrong type. Please provide str, tuple[str, str] or list[tuple[str, str]].
"""

LITERAL_AND_EXPRESSION_MISSING = """
Can't create {clause} query without providing either 'literal' or 'expression' keyword arguments,
that can be literals, labels or properties.
"""

EXTRA_KEYWORD_ARGUMENTS = """
Can't create {clause} query with extra keyword arguments:
Please provide a value to either 'literal' or 'expression' keyword arguments.
"""

RESULT_QUERY_TYPE_ERROR = """
Can't create {clause} query:
The argument provided is of wrong type. Please provide str, tuple[str, str], list[Union[tuple[str, str], str]] or set[Union[tuple[str, str], str]].
"""

INSTANTIATION_ERROR = """
{class_name} class shouldn't be instantiated!
"""

TOO_LARGE_TUPLE_IN_RESULT_QUERY = """
Tuple argument in {clause} clause only has two arguments - variable name and alias.
"""

FILE_NOT_FOUND = """
File with path {path} not found.
"""

OPERATOR_TYPE_ERROR = """
Operator argument in {clause} clause that is a string must be a valid operator.
"""

TIMEOUT_ERROR_MESSAGE = "Waited too long for the port {port} on host {host} to start accepting connections."
DOCKER_TIMEOUT_ERROR_MESSAGE = "Waited too long for the Docker container to start."
MEMGRAPH_CONNECTION_ERROR_MESSAGE = "The Memgraph process probably died."


class QueryClause(Enum):
    WHERE = "WHERE"
    SET = "SET"


class GQLAlchemyWarning(Warning):
    pass


class GQLAlchemySubclassNotFoundWarning(GQLAlchemyWarning):
    def __init__(self, types, cls):
        self.message = SUBCLASS_NOT_FOUND_WARNING.format(types=types, cls=cls)


class GQLAlchemyError(Exception):
    pass


class GQLAlchemyUniquenessConstraintError(GQLAlchemyError):
    pass


class GQLAlchemyDatabaseMissingInFieldError(GQLAlchemyError):
    def __init__(self, constraint: str, field: str, field_type: str):
        self.message = DATABASE_MISSING_IN_FIELD_ERROR_MESSAGE.format(
            constraint=constraint,
            field=field,
            field_type=field_type,
        )


class GQLAlchemyDatabaseMissingInNodeClassError(GQLAlchemyError):
    def __init__(self, cls):
        self.message = DATABASE_MISSING_IN_NODE_CLASS_ERROR_MESSAGE.format(cls=cls)


class GQLAlchemyOnDiskPropertyDatabaseNotDefinedError(GQLAlchemyError):
    def __init__(self):
        self.message = ON_DISK_PROPERTY_DATABASE_NOT_DEFINED_ERROR


class GQLAlchemyMissingOrder(GQLAlchemyError):
    def __init__(self):
        self.message = MISSING_ORDER


class GQLAlchemyOrderByTypeError(GQLAlchemyError):
    def __init__(self):
        self.message = ORDER_BY_TYPE_ERROR


class GQLAlchemyLiteralAndExpressionMissing(GQLAlchemyError):
    def __init__(self, clause: str):
        self.message = LITERAL_AND_EXPRESSION_MISSING.format(clause=clause)


class GQLAlchemyExtraKeywordArguments(GQLAlchemyError):
    def __init__(self, clause: str):
        self.message = EXTRA_KEYWORD_ARGUMENTS.format(clause=clause)


class GQLAlchemyTooLargeTupleInResultQuery(GQLAlchemyError):
    def __init__(self, clause) -> None:
        self.message = TOO_LARGE_TUPLE_IN_RESULT_QUERY.format(clause=clause)


class GQLAlchemyResultQueryTypeError(GQLAlchemyError):
    def __init__(self, clause):
        self.message = RESULT_QUERY_TYPE_ERROR.format(clause=clause)


class GQLAlchemyInstantiationError(GQLAlchemyError):
    def __init__(self, class_name) -> None:
        self.message = INSTANTIATION_ERROR.format(class_name=class_name)


class GQLAlchemyDatabaseError(GQLAlchemyError):
    def __init__(self, message):
        self.message = message


class GQLAlchemyOperatorTypeError(GQLAlchemyError):
    def __init__(self, clause) -> None:
        self.message = OPERATOR_TYPE_ERROR.format(clause=clause)


class GQLAlchemyTimeoutError(GQLAlchemyError):
    def __init__(self, message):
        self.message = message


class GQLAlchemyWaitForPortError(GQLAlchemyTimeoutError):
    def __init__(self, port, host):
        super().__init__(message=TIMEOUT_ERROR_MESSAGE.format(port=port, host=host))


class GQLAlchemyWaitForDockerError(GQLAlchemyTimeoutError):
    def __init__(self):
        super().__init__(message=DOCKER_TIMEOUT_ERROR_MESSAGE)


class GQLAlchemyWaitForConnectionError(GQLAlchemyTimeoutError):
    def __init__(self):
        super().__init__(message=MEMGRAPH_CONNECTION_ERROR_MESSAGE)


class GQLAlchemyFileNotFoundError(GQLAlchemyError):
    def __init__(self, path):
        super().__init__()
        self.message = FILE_NOT_FOUND.format(path=path)


def raise_if_not_imported(dependency, dependency_name):
    if not dependency:
        raise ModuleNotFoundError(MISSING_OPTIONAL_DEPENDENCY.format(dependency_name=dependency_name))


def database_error_handler(func):
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise GQLAlchemyDatabaseError(e) from e

    return inner_function


def connection_handler(func, delay: float = 0.01, timeout: float = 5.0, backoff: int = 2):
    """Wrapper for a wait on the connection.

    Args:
        func: A function that tries to create the connection
        delay: A float that defines how long to wait between retries.
        timeout: A float that defines how long to wait for the port.
        backoff: An integer used for multiplying the delay.

    Raises:
      GQLAlchemyWaitForConnectionError: Raises an error
      after the timeout period has passed.
    """

    def _handler(*args, **kwargs):
        start_time = time.perf_counter()
        current_delay = delay
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                time.sleep(current_delay)
                if time.perf_counter() - start_time >= timeout:
                    raise GQLAlchemyWaitForConnectionError from ex

                current_delay *= backoff

    return _handler
