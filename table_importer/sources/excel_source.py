
from collections.abc import Iterator
from itertools import islice
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from .base import DataSource
from ..metadata import TableMetadata
from ..exceptions import (
    SourceNotFoundError,
    TableNotFoundError,
    SourceReadError,
)

class ExcelSource(DataSource):
    """
    Источник табличных данных в формате XLSX.

    Поддерживает несколько листов, предварительное
    сканирование и чтение данных по частям.
    """

    def __init__(self, path: str | Path):
        """
        Сохраняет путь к Excel-файлу.

        Проверяет существование файла, но не загружает
        его содержимое в оперативную память.
        """
        self.path = Path(path)

        if not self.path.is_file():
            raise SourceNotFoundError(
                f"Excel-файл не найден: {self.path}"
            )

    def get_tables(self) -> list[str]:
        """
        Возвращает названия всех листов Excel-файла.

        Для получения названий используется структура
        рабочей книги без чтения всех строк таблиц.
        """
        workbook = load_workbook(
            self.path,
            read_only=True,
            data_only=True
        )

        try:
            return list(workbook.sheetnames)
        finally:
            workbook.close()

    def scan(
        self,
        table: str,
        limit: int = 1000
    ) -> dict:
        """
        Сканирует ограниченное количество строк листа.

        Первая строка считается заголовком таблицы.

        Возвращает названия столбцов, предполагаемые
        типы данных и количество пропусков в выборке.
        """
        if limit <= 0:
            raise ValueError(
                "Количество строк для сканирования должно быть положительным"
            )

        workbook = load_workbook(
            self.path,
            read_only=True,
            data_only=True
        )

        try:
            if table not in workbook.sheetnames:
                raise TableNotFoundError(
                    f"Лист '{table}' не найден. "
                    f"Доступные листы: {workbook.sheetnames}"
                )

            worksheet = workbook[table]
            total_rows = max(
                worksheet.max_row - 1,
                0
                    )
            rows = worksheet.iter_rows(values_only=True)

            # Первая строка содержит названия столбцов.
            headers = next(rows, None)

            if headers is None:
                return {
                    "name": table,
                    "sampled_rows": 0,
                    "columns": [],
                    "dtypes": {},
                    "missing_values": {}
                }

            # Читаем не больше limit строк данных.
            sample_rows = list(islice(rows, limit))

            sample = pd.DataFrame(
                sample_rows,
                columns=headers
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

            missing_values=
                sample.isna().sum().to_dict(),

            size_is_estimated=False
        ) 
            return metadata.to_dict()
        finally:
            workbook.close()

    def iter_chunks(
        self,
        table: str,
        chunk_size: int = 10000
    ) -> Iterator[pd.DataFrame]:
        """
        Последовательно читает Excel-лист частями.

        Каждая часть содержит не более chunk_size строк.
        Чтение выполняется в потоковом режиме.

        Возвращает итератор объектов pandas.DataFrame.
        """
        if chunk_size <= 0:
            raise TableNotFoundError(
                "Размер части должен быть положительным"
            )

        workbook = load_workbook(
            self.path,
            read_only=True,
            data_only=True
        )

        try:
            if table not in workbook.sheetnames:
                raise ValueError(
                    f"Лист '{table}' не найден. "
                    f"Доступные листы: {workbook.sheetnames}"
                )

            worksheet = workbook[table]

            rows = worksheet.iter_rows(values_only=True)

            # Получаем заголовки из первой строки.
            headers = next(rows, None)

            if headers is None:
                return

            # Накапливаем только одну часть данных.
            buffer = []

            for row in rows:
                buffer.append(row)

                if len(buffer) == chunk_size:
                    yield pd.DataFrame(
                        buffer,
                        columns=headers
                    )

                    buffer = []

            # Возвращаем последнюю неполную часть.
            if buffer:
                yield pd.DataFrame(
                    buffer,
                    columns=headers
                )
        finally:
            workbook.close()
