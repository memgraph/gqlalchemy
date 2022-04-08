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
        super().__init__()
        self.message = DATABASE_MISSING_IN_FIELD_ERROR_MESSAGE.format(
            constraint=constraint,
            field=field,
            field_type=field_type,
        )


class GQLAlchemyDatabaseMissingInNodeClassError(GQLAlchemyError):
    def __init__(self, cls):
        super().__init__()
        self.message = DATABASE_MISSING_IN_NODE_CLASS_ERROR_MESSAGE.format(cls=cls)


class GQLAlchemyOnDiskPropertyDatabaseNotDefinedError(GQLAlchemyError):
    def __init__(self):
        super().__init__()
        self.message = ON_DISK_PROPERTY_DATABASE_NOT_DEFINED_ERROR


class GQLAlchemyMissingOrder(GQLAlchemyError):
    def __init__(self):
        super().__init__()
        self.message = MISSING_ORDER


class GQLAlchemyOrderByTypeError(TypeError):
    def __init__(self):
        super().__init__()
        self.message = ORDER_BY_TYPE_ERROR


class GQLAlchemyLiteralAndExpressionMissingInClause(GQLAlchemyError):
    def __init__(self, clause: str):
        super().__init__()
        self.message = LITERAL_AND_EXPRESSION_MISSING.format(clause=clause)


class GQLAlchemyLiteralAndExpressionMissingInWhere(GQLAlchemyLiteralAndExpressionMissingInClause):
    def __init__(self):
        super().__init__(clause="WHERE")


class GQLAlchemyLiteralAndExpressionMissingInSet(GQLAlchemyLiteralAndExpressionMissingInClause):
    def __init__(self):
        super().__init__(clause="SET")


class GQLAlchemyExtraKeywordArguments(GQLAlchemyError):
    def __init__(self, clause: str):
        super().__init__()
        self.message = EXTRA_KEYWORD_ARGUMENTS.format(clause=clause)


class GQLAlchemyExtraKeywordArgumentsInWhere(GQLAlchemyExtraKeywordArguments):
    def __init__(self):
        super().__init__(clause="WHERE")


class GQLAlchemyExtraKeywordArgumentsInSet(GQLAlchemyExtraKeywordArguments):
    def __init__(self):
        super().__init__(clause="SET")
