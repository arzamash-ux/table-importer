
from pathlib import Path

import pandas as pd

from .sources.base import DataSource
from .sources.csv_source import CSVSource
from .sources.excel_source import ExcelSource
from .sources.sqlite_source import SQLiteSource
class TableImporter:
    """
    Основной класс библиотеки для импорта табличных данных.

    Предоставляет единый интерфейс для работы
    с различными источниками данных.
    """

    def __init__(self, path: str | Path):
        """
        Создаёт импортёр и определяет тип источника.

        :param path: Путь к файлу с данными.
        """
        self.path = Path(path)
        self.source = self._create_source()

    
    
    def _create_source(self) -> DataSource:
        """
        Создаёт подходящий источник по расширению файла.

        Поддерживает CSV, XLSX и SQLite.
        """
        extension = self.path.suffix.lower()

        if extension == ".csv":
            return CSVSource(self.path)

        if extension == ".xlsx":
            return ExcelSource(self.path)

        if extension in {".db", ".sqlite", ".sqlite3"}:
            return SQLiteSource(self.path)

        raise ValueError(
            f"Неподдерживаемый формат файла: {extension}"
        )

    def get_tables(self) -> list[str]:
        """
        Возвращает названия доступных таблиц.

        :return: Список названий таблиц.
        """
        return self.source.get_tables()

    def scan(
        self,
        table: str | None = None,
        limit: int = 1000
    ) -> dict:
        """
        Выполняет предварительное сканирование таблицы.

        Если название таблицы не указано, выбирается первая.

        :param table: Название таблицы.
        :param limit: Максимальное число строк для анализа.
        :return: Словарь с метаданными.
        """
        table = self._resolve_table(table)

        return self.source.scan(table, limit)
    
    def _resolve_table(self, table: str | None) -> str:
        """
        Определяет таблицу для работы.

        Если источник содержит одну таблицу,
        она выбирается автоматически.

        Если таблиц несколько, пользователь
        обязан указать название.
        """
        tables = self.get_tables()

        if table is not None:
            if table not in tables:
                raise ValueError(
                    f"Таблица '{table}' не найдена. "
                    f"Доступные таблицы: {tables}"
                )

            return table

        if not tables:
            raise ValueError(
                "Источник не содержит доступных таблиц"
            )

        if len(tables) == 1:
            return tables[0]

        raise ValueError(
            "Источник содержит несколько таблиц. "
            f"Укажите table. Доступные таблицы: {tables}"
        )

    def load(
        self,
        table: str | None = None,
        chunk_size: int = 10000
    ) -> pd.DataFrame:
        """
        Загружает таблицу по частям и объединяет результат.

        :param table: Название таблицы.
        :param chunk_size: Количество строк в одной части.
        :return: Итоговый pandas DataFrame.
        """
        table = self._resolve_table(table)

        chunks = []

        for chunk in self.source.iter_chunks(
            table,
            chunk_size
        ):
            chunks.append(chunk)

        if not chunks:
            return pd.DataFrame()

        return pd.concat(
            chunks,
            ignore_index=True
        )
