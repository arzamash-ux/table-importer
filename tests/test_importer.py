
import pandas as pd
import pytest

from table_importer import TableImporter
from table_importer.exceptions import UnsupportedSourceError

def test_importer_scan(tmp_path):
    """
    Проверяет получение метаданных
    через единый интерфейс.
    """

    path = tmp_path / "users.csv"

    data = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })

    data.to_csv(
        path,
        index=False
    )

    importer = TableImporter(path)

    metadata = importer.scan(
        limit=2
    )

    assert metadata["name"] == "users"

    assert metadata["rows"]["sampled"] == 2

    assert metadata["columns"]["names"] == [
        "id",
        "name"
    ]

def test_importer_load(tmp_path):
    """
    Проверяет загрузку CSV по частям и сборку DataFrame.
    """
    path = tmp_path / "users.csv"

    expected = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["A", "B", "C", "D", "E"]
    })

    expected.to_csv(path, index=False)

    importer = TableImporter(path)

    result = importer.load(chunk_size=2)

    pd.testing.assert_frame_equal(
        result,
        expected
    )



def test_unsupported_source(tmp_path):
    """
    Проверяет ошибку при попытке открыть файл
    неподдерживаемого формата.
    """
    path = tmp_path / "data.txt"

    # Создаём файл с неподдерживаемым расширением.
    path.write_text("test", encoding="utf-8")

    # Проверяем, что возникает наше исключение.
    with pytest.raises(
        UnsupportedSourceError,
        match="Неподдерживаемый формат"
    ):
        TableImporter(path)
