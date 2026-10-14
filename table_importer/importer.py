
from pathlib import Path

import pandas as pd

from .sources.base import DataSource
from .sources.csv_source import CSVSource
from .sources.excel_source import ExcelSource
from .sources.sqlite_source import SQLiteSource
from .session import ImportSession
from .exceptions import UnsupportedSourceError
from .exceptions import TableNotFoundError
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

        raise UnsupportedSourceError(
            f"Неподдерживаемый формат файла: {extension}"
            )
    
    
    def create_session(
        self,
        table: str | None = None,
        chunk_size: int = 10000,
        dtype: dict[str, str] | None = None,
        conversion_errors: str = "raise"
    ) -> ImportSession:
        """
        Создаёт сессию импорта данных.

        Аргументы:
            table: Название таблицы или листа.
            chunk_size: Размер одной части.
            dtype: Требуемые типы столбцов.
            conversion_errors: Режим обработки ошибок.

        Возвращает:
            Объект ImportSession.
        """
        if chunk_size <= 0:
            raise ValueError(
                "Размер части должен быть положительным"
            )

        table = self._resolve_table(table)

        chunks = self.source.iter_chunks(
            table=table,
            chunk_size=chunk_size
        )

        return ImportSession(
            chunks=chunks,
            dtype=dtype,
            conversion_errors=conversion_errors
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
        Определяет таблицу для выполнения операции.

        Если таблица одна, выбирает её автоматически.
        Если таблиц несколько, требует явного выбора.
        """
        available_tables = self.get_tables()

        if table is not None:
            if table not in available_tables:
                raise TableNotFoundError(
                    f"Таблица '{table}' не найдена. "
                    f"Доступные таблицы: {available_tables}"
                )

            return table

        if not available_tables:
            raise TableNotFoundError(
                "Источник данных не содержит таблиц"
            )

        if len(available_tables) == 1:
            return available_tables[0]

        raise ValueError(
            "Источник содержит несколько таблиц. "
            f"Укажите table. Доступные таблицы: {available_tables}"
        )


    
    
    def load(
        self,
        table: str | None = None,
        chunk_size: int = 10000,
        dtype: dict[str, str] | None = None,
        conversion_errors: str = "raise"
    ) -> pd.DataFrame:
        """
        Полностью загружает таблицу в DataFrame.

        При необходимости преобразует типы столбцов.
        """
        session = self.create_session(
            table=table,
            chunk_size=chunk_size,
            dtype=dtype,
            conversion_errors=conversion_errors
        )

        return session.load_all()
