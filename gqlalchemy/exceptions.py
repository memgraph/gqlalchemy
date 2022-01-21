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


class GQLAlchemyOnDiskPropertyDatabaseNotDefinedError(GQLAlchemyError):
    def __init__(self):
        super().__init__()
        self.message = ON_DISK_PROPERTY_DATABASE_NOT_DEFINED_ERROR
