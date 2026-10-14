import sqlite3

from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from .base import DataSource
from ..metadata import TableMetadata
from ..exceptions import (
    SourceNotFoundError,
    TableNotFoundError,
    SourceReadError,
)

class SQLiteSource(DataSource):
    """
    Источник табличных данных из базы SQLite.

    Поддерживает получение списка таблиц,
    предварительное сканирование и
    итерационную загрузку данных.
    """

    def __init__(self, path: str | Path):
        """
        Сохраняет путь к базе данных.

        Проверяет существование файла, чтобы
        случайно не создать пустую базу данных.
        """
        self.path = Path(path)

        if not self.path.is_file():
            raise SourceNotFoundError(
                f"База данных SQLite не найдена: {self.path}"
            )

    def _connect(self) -> sqlite3.Connection:
        """
        Открывает соединение с существующей базой.

        Режим mode=ro запрещает изменение
        содержимого базы данных.
        """
        uri = self.path.resolve().as_uri() + "?mode=ro"

        return sqlite3.connect(
            uri,
            uri=True
        )

    def get_tables(self) -> list[str]:
        """
        Возвращает имена пользовательских таблиц.

        Системные таблицы SQLite исключаются.
        """
        with self._connect() as connection:
            cursor = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    def _validate_table(self, table: str) -> None:
        """
        Проверяет существование таблицы.

        Защищает от обращения к отсутствующим
        таблицам и использования произвольного
        SQL вместо имени таблицы.
        """
        available_tables = self.get_tables()

        if table not in available_tables:
            raise TableNotFoundError(
                f"Таблица '{table}' не найдена. "
                f"Доступные таблицы: {available_tables}"
            )

    def _quoted_table(self, table: str) -> str:
        """
        Безопасно экранирует имя таблицы SQLite.

        Имена таблиц нельзя передавать через
        SQL-параметры ?, поэтому используются
        проверка имени и экранирование кавычек.
        """
        self._validate_table(table)

        escaped = table.replace('"', '""')

        return f'"{escaped}"'

    def scan(self, table: str,
            limit: int = 1000
            ) -> dict:
            """
            Сканирует ограниченное количество строк таблицы.

            Возвращает метаданные:
            - количество строк;
            - список столбцов;
            - типы данных;
            - количество пропусков.
            """

            if limit <= 0:
                    raise ValueError(
                    "Количество строк должно быть положительным"
                )

            quoted_table = self._quoted_table(table)

            # Запрос для получения количества строк.
            count_query = f"""
                SELECT COUNT(*)
                FROM {quoted_table}
            """

            # Запрос для получения выборки.
            sample_query = f"""
                SELECT *
                FROM {quoted_table}
                LIMIT ?
            """

            with self._connect() as connection:

                # Узнаём полный размер таблицы.
                total_rows = connection.execute(
                    count_query
                ).fetchone()[0]


                # Получаем только часть данных.
                sample = pd.read_sql_query(
                    sample_query,
                    connection,
                    params=(limit,)
                )


            metadata = TableMetadata(

                name=table,

                total_rows=total_rows,

                sampled_rows=len(sample),

                columns_count=len(sample.columns),

                columns=list(sample.columns),

                dtypes={
                    name: str(dtype)
                    for name, dtype in sample.dtypes.items()
                },

                missing_values=(
                    sample.isna()
                    .sum()
                    .to_dict()
                ),

                size_is_estimated=False
            )
            return metadata.to_dict()

    def iter_chunks(
        self,
        table: str,
        chunk_size: int = 10000
    ) -> Iterator[pd.DataFrame]:
        """
        Последовательно загружает таблицу частями.

        SQLite не загружает всю таблицу сразу.
        Каждая часть возвращается как DataFrame.
        """
        if chunk_size <= 0:
            raise ValueError(
                "Размер части должен быть положительным"
            )

        quoted_table = self._quoted_table(table)

        query = f"SELECT * FROM {quoted_table}"

        # Соединение остаётся открытым,
        # пока генератор возвращает части данных.
        connection = self._connect()

        try:
            reader = pd.read_sql_query(
                query,
                connection,
                chunksize=chunk_size
            )

            yield from reader

        finally:
            # Закрываем соединение после завершения
            # чтения или закрытия генератора.
            connection.close()
