from dataclasses import dataclass


@dataclass
class TableMetadata:
    """
    Метаданные одной таблицы.

    Используются при предварительном сканировании.
    """

    name: str

    # Количество строк.
    total_rows: int | None

    # Сколько строк реально просмотрели.
    sampled_rows: int

    # Количество столбцов.
    columns_count: int

    # Названия столбцов.
    columns: list[str]

    # Типы данных.
    dtypes: dict[str, str]

    # Количество пропусков.
    missing_values: dict[str, int]

    # Размер точный или приблизительный.
    size_is_estimated: bool = False


    def to_dict(self) -> dict:
        """
        Преобразует объект в обычный словарь.

        Удобно для JSON и README.
        """

        return {
            "name": self.name,

            "rows": {
                "sampled": self.sampled_rows,
                "total": self.total_rows,
                "estimated": self.size_is_estimated
            },

            "columns": {
                "count": self.columns_count,
                "names": self.columns
            },

            "dtypes": self.dtypes,

            "missing_values": self.missing_values
        }