
import pandas as pd
import pytest

from table_importer import (
    TableImporter,
    DataConversionError
)


def test_float_conversion(tmp_path):
    """
    Проверяет преобразование строк в числа.
    """
    path = tmp_path / "prices.csv"

    pd.DataFrame({
        "price": ["100.50", "200.75", "300.25"]
    }).to_csv(path, index=False)

    importer = TableImporter(path)

    result = importer.load(
        chunk_size=2,
        dtype={"price": "float64"}
    )

    assert str(result["price"].dtype) == "float64"
    assert result["price"].tolist() == [
        100.50, 200.75, 300.25
    ]


def test_datetime_conversion(tmp_path):
    """
    Проверяет преобразование строк в даты.
    """
    path = tmp_path / "dates.csv"

    pd.DataFrame({
        "created_at": [
            "2026-01-01",
            "2026-02-15"
        ]
    }).to_csv(path, index=False)

    importer = TableImporter(path)

    result = importer.load(
        chunk_size=1,
        dtype={"created_at": "datetime64[ns]"}
    )

    assert pd.api.types.is_datetime64_any_dtype(
        result["created_at"]
    )


def test_conversion_error_raise(tmp_path):
    """
    Проверяет ошибку при некорректном числе.
    """
    path = tmp_path / "invalid.csv"

    pd.DataFrame({
        "price": ["100", "invalid", "300"]
    }).to_csv(path, index=False)

    importer = TableImporter(path)

    with pytest.raises(
        DataConversionError,
        match="price"
    ):
        importer.load(
            chunk_size=2,
            dtype={"price": "float64"},
            conversion_errors="raise"
        )


def test_conversion_error_coerce(tmp_path):
    """
    Проверяет замену ошибочных значений
    на пропуски при преобразовании.
    """
    path = tmp_path / "invalid.csv"

    pd.DataFrame({
        "price": ["100", "invalid", "300"]
    }).to_csv(path, index=False)

    importer = TableImporter(path)

    result = importer.load(
        chunk_size=2,
        dtype={"price": "float64"},
        conversion_errors="coerce"
    )

    assert result["price"].iloc[0] == 100.0
    assert pd.isna(result["price"].iloc[1])
    assert result["price"].iloc[2] == 300.0


def test_unknown_column_conversion(tmp_path):
    """
    Проверяет ошибку при указании
    несуществующего столбца.
    """
    path = tmp_path / "users.csv"

    pd.DataFrame({
        "id": [1, 2, 3]
    }).to_csv(path, index=False)

    importer = TableImporter(path)

    with pytest.raises(
        DataConversionError,
        match="age"
    ):
        importer.load(
            dtype={"age": "Int64"}
        )
