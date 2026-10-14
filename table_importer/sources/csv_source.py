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

class CSVSource(DataSource):
    """Источник данных для CSV-файлов."""

    def __init__(self, path: str | Path):
        """Инициализировать CSV-источник и проверить путь."""
        self.path = Path(path)

        if not self.path.is_file():
            raise SourceNotFoundError(
                f"CSV-файл не найден: {self.path}"
            )

    def get_tables(self) -> list[str]:
        """Вернуть единственное имя таблицы для этого CSV-файла."""
        return [self.path.stem]

    
    def scan(self, table: str, limit: int = 1000) -> dict:
        """
        Выполняет частичное сканирование CSV-файла.

        При ошибке чтения возвращает специальное
        исключение с указанием источника.
        """
        if limit <= 0:
            raise ValueError(
                "Количество строк должно быть положительным"
            )

        if table not in self.get_tables():
            raise TableNotFoundError(
                f"Таблица '{table}' не найдена"
            )

        try:
            sample = pd.read_csv(
                self.path,
                nrows=limit
            )

        except (pd.errors.ParserError, pd.errors.EmptyDataError,
                UnicodeError, OSError) as error:
            raise SourceReadError(
                f"Не удалось прочитать CSV-файл "
                f"'{self.path}'. Причина: {error}"
            ) from error

        metadata = TableMetadata(

            name=table,

            total_rows=None,

            sampled_rows=len(sample),

            columns_count=len(sample.columns),

            columns=list(sample.columns),

            dtypes={
                name: str(dtype)
                for name, dtype in sample.dtypes.items()
            },

            missing_values=
                sample.isna().sum().to_dict(),

            size_is_estimated=True
        )


        return metadata.to_dict()


    def iter_chunks(
        self,
        table: str,
        chunk_size: int = 10000
    ) -> Iterator[pd.DataFrame]:
        """Выдавать последовательные порции CSV в виде DataFrame."""
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")

        if table not in self.get_tables():
            raise ValueError(f"Unknown table: {table}")

        yield from pd.read_csv(
            self.path,
            chunksize=chunk_size
        )