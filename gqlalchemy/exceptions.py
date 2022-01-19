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
    def __init__(self, constraint, field, field_type):
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
