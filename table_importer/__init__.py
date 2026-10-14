
"""
Библиотека для импорта табличных данных.
"""

from .importer import TableImporter
from .session import ImportSession

from .exceptions import (
    TableImporterError,
    UnsupportedSourceError,
    SourceNotFoundError,
    TableNotFoundError,
    DataConversionError,
    SourceReadError,
)

__all__ = [
    "TableImporter",
    "ImportSession",
    "TableImporterError",
    "UnsupportedSourceError",
    "SourceNotFoundError",
    "TableNotFoundError",
    "DataConversionError",
    "SourceReadError",
]
