
import pandas as pd

from table_importer import TableImporter


def test_excel_multiple_sheets(tmp_path):
    """
    Проверяет получение названий нескольких листов.
    """
    path = tmp_path / "sales.xlsx"

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame({
            "id": [1, 2],
            "price": [100, 200]
        }).to_excel(
            writer,
            sheet_name="January",
            index=False
        )

        pd.DataFrame({
            "id": [3, 4],
            "price": [300, 400]
        }).to_excel(
            writer,
            sheet_name="February",
            index=False
        )

    importer = TableImporter(path)

    assert importer.get_tables() == [
        "January",
        "February"
    ]


def test_excel_scan(tmp_path):
    """
    Проверяет сканирование ограниченного числа строк.
    """
    path = tmp_path / "sales.xlsx"

    data = pd.DataFrame({
        "id": [1, 2, 3],
        "price": [100, None, 300]
    })

    data.to_excel(path, index=False)

    importer = TableImporter(path)

    metadata = importer.scan(limit=2)

    assert metadata["rows"]["sampled"] == 2
    assert metadata["columns"]["names"] == [
    "id",
    "price"
]
    assert metadata["missing_values"]["price"] == 1


def test_excel_chunking(tmp_path):
    """
    Проверяет загрузку Excel по частям.
    """
    path = tmp_path / "sales.xlsx"

    expected = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "price": [10, 20, 30, 40, 50]
    })

    expected.to_excel(path, index=False)

    importer = TableImporter(path)

    result = importer.load(chunk_size=2)

    pd.testing.assert_frame_equal(
        result,
        expected
    )
