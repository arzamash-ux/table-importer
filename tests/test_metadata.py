import pandas as pd

from table_importer import TableImporter


def test_csv_metadata(tmp_path):

    path = tmp_path / "users.csv"

    pd.DataFrame(
        {
            "id":[1,2,3],
            "name":["A","B","C"]
        }
    ).to_csv(
        path,
        index=False
    )


    importer = TableImporter(path)


    metadata = importer.scan()


    assert metadata["name"] == "users"

    assert metadata["columns"]["count"] == 2

    assert metadata["rows"]["sampled"] == 3

    assert metadata["rows"]["estimated"] is True



def test_excel_metadata(tmp_path):

    path = tmp_path / "users.xlsx"


    pd.DataFrame(
        {
            "id":[1,2,3]
        }
    ).to_excel(
        path,
        index=False
    )


    importer = TableImporter(path)


    metadata = importer.scan()


    assert metadata["rows"]["total"] == 3

    assert metadata["rows"]["estimated"] is False