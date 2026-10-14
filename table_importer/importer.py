
from pathlib import Path

import pandas as pd

from .sources.base import DataSource
from .sources.csv_source import CSVSource
from .sources.excel_source import ExcelSource

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
        Выбирает класс источника по расширению файла.

        Сейчас поддерживаются CSV и XLSX.
        """
        extension = self.path.suffix.lower()

        if extension == ".csv":
            return CSVSource(self.path)

        if extension == ".xlsx":
            return ExcelSource(self.path)

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
        if table is None:
            table = self.get_tables()[0]

        return self.source.scan(table, limit)

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
        if table is None:
            table = self.get_tables()[0]

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
