"""Semantic errors for persistence infrastructure."""


class PersistenceError(Exception):
    """Base persistence error."""


class SchemaError(PersistenceError):
    """Schema inspection or initialization error."""


class UnsupportedNewerSchemaError(SchemaError):
    """Raised when the database schema is newer than this application supports."""
