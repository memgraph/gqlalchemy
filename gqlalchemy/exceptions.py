DATABASE_MISSING_IN_FIELD_ERROR_MESSAGE = """
Can't have an index on a property without providing the database `db` object.
Define your property as:
  {field}: {field_type} = Field({constraint}=True, db=GraphDatabase())
"""

SUBCLASS_NOT_FOUND_WARNING = """
GraphObject subclass(es) '{types}' not found.
'{cls.__name__}' will be used until you create a subclass.
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
        self.message = DATABASE_MISSING_IN_FIELD_ERROR_MESSAGE.format(
            constraint=constraint,
            field=field,
            field_type=field_type,
        )
