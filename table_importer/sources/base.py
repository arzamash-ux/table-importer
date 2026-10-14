from abc import ABC, abstractmethod
from collections.abc import Iterator

import pandas as pd


class DataSource(ABC):
    """
    Абстрактный интерфейс для табличных источников данных.

    Каждый источник данных должен поддерживать:
    - получение списка доступных таблиц;
    - сканирование метаданных таблицы;
    - чтение данных порциями (чанками).
    """

    @abstractmethod
    def get_tables(self) -> list[str]:
        """
        Вернуть имена доступных таблиц.

        CSV: одна таблица.
        Excel: имена листов.
        SQLite: имена таблиц базы данных.
        """
        pass

    @abstractmethod
    def scan(self, table: str, limit: int) -> dict:
        """
        Просканировать ограниченное количество строк.

        Аргументы:
            table: Имя таблицы.
            limit: Максимальное количество строк для просмотра.

        Возвращает:
            Словарь с метаданными таблицы.
        """
        pass

    @abstractmethod
    def iter_chunks(
        self,
        table: str,
        chunk_size: int
    ) -> Iterator[pd.DataFrame]:
        """
        Читать таблицу порциями (чанками).

        Аргументы:
            table: Имя таблицы.
            chunk_size: Количество строк в одной порции.

        Yields:
            pandas DataFrame, содержащий следующую порцию данных.
        """
        pass