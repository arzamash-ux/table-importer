
import sqlite3

import pandas as pd
import pytest

from table_importer import TableImporter
from table_importer.exceptions import (
    SourceNotFoundError,
    TableNotFoundError,
)

@pytest.fixture
def sqlite_database(tmp_path):
    """
    Создаёт временную базу SQLite для тестов.

    В базе будут две таблицы:
    users и orders.
    """
    path = tmp_path / "shop.db"

    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE users (
                id INTEGER,
                name TEXT,
                age INTEGER
            )
            """
        )

        connection.executemany(
            "INSERT INTO users VALUES (?, ?, ?)",
            [
                (1, "Alice", 20),
                (2, "Bob", None),
                (3, "Charlie", 30),
                (4, "David", 25),
                (5, "Eva", 28)
            ]
        )

        connection.execute(
            """
            CREATE TABLE orders (
                id INTEGER,
                amount REAL
            )
            """
        )

        connection.executemany(
            "INSERT INTO orders VALUES (?, ?)",
            [
                (1, 150.5),
                (2, 200.0)
            ]
        )

    return path


def test_sqlite_get_tables(sqlite_database):
    """
    Проверяет получение списка таблиц SQLite.
    """
    importer = TableImporter(sqlite_database)

    tables = importer.get_tables()

    assert tables == ["orders", "users"]


def test_sqlite_scan(sqlite_database):
    """
    Проверяет ограниченное сканирование таблицы.
    """
    importer = TableImporter(sqlite_database)

    metadata = importer.scan(
        table="users",
        limit=3
    )

    assert metadata["name"] == "users"
    assert metadata["sampled_rows"] == 3
    assert metadata["columns"] == [
        "id", "name", "age"
    ]
    assert metadata["missing_values"]["age"] == 1


def test_sqlite_load(sqlite_database):
    """
    Проверяет загрузку таблицы в DataFrame.
    """
    importer = TableImporter(sqlite_database)

    result = importer.load(
        table="users",
        chunk_size=2
    )

    assert len(result) == 5
    assert list(result.columns) == [
        "id", "name", "age"
    ]
    assert result["name"].tolist() == [
        "Alice", "Bob", "Charlie", "David", "Eva"
    ]


def test_sqlite_chunks(sqlite_database):
    """
    Проверяет количество частей при чтении SQLite.
    """
    from table_importer.sources.sqlite_source import SQLiteSource

    source = SQLiteSource(sqlite_database)

    chunks = list(
        source.iter_chunks("users", chunk_size=2)
    )

    assert len(chunks) == 3

    assert [len(chunk) for chunk in chunks] == [
        2, 2, 1
    ]


def test_sqlite_unknown_table(sqlite_database):
    """
    Проверяет ошибку для несуществующей таблицы.
    """
    importer = TableImporter(sqlite_database)

    with pytest.raises(
        TableNotFoundError,
        match="не найдена"
    ):
        importer.scan(
            table="unknown",
            limit=10
        )


def test_sqlite_missing_database(tmp_path):
    """
    Проверяет, что отсутствующая база
    не создаётся автоматически.
    """
    path = tmp_path / "missing.db"

    with pytest.raises(SourceNotFoundError):
        TableImporter(path)

    assert not path.exists()
