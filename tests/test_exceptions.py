
import pytest

from table_importer import (
    TableImporter,
    TableImporterError,
    SourceNotFoundError,
    TableNotFoundError,
    UnsupportedSourceError,
)


def test_missing_csv_file(tmp_path):
    """
    Проверяет обработку отсутствующего CSV-файла.
    """
    path = tmp_path / "missing.csv"

    with pytest.raises(SourceNotFoundError):
        TableImporter(path)


def test_missing_excel_file(tmp_path):
    """
    Проверяет обработку отсутствующего Excel-файла.
    """
    path = tmp_path / "missing.xlsx"

    with pytest.raises(SourceNotFoundError):
        TableImporter(path)


def test_missing_sqlite_file(tmp_path):
    """
    Проверяет обработку отсутствующей SQLite-базы.
    """
    path = tmp_path / "missing.db"

    with pytest.raises(SourceNotFoundError):
        TableImporter(path)


def test_exception_inheritance():
    """
    Проверяет, что собственные исключения
    наследуются от общего базового класса.
    """
    assert issubclass(
        SourceNotFoundError,
        TableImporterError
    )

    assert issubclass(
        TableNotFoundError,
        TableImporterError
    )

    assert issubclass(
        UnsupportedSourceError,
        TableImporterError
    )
