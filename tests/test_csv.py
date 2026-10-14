
import pandas as pd

from table_importer.sources.csv_source import CSVSource


def test_csv_scan(tmp_path):
    """Check that scanning extracts sample metadata."""
    path = tmp_path / "users.csv"

    data = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", None],
        "age": [20, 25, 30]
    })

    data.to_csv(path, index=False)

    source = CSVSource(path)
    metadata = source.scan("users", limit=2)

    assert metadata["rows"]["sampled"] == 2
    assert metadata["columns"]["names"] == [
    "id",
    "name",
    "age"
]
    assert metadata["missing_values"]["name"] == 0


def test_csv_chunking(tmp_path):
    """Check that the CSV source reads rows in chunks."""
    path = tmp_path / "users.csv"

    pd.DataFrame({
        "id": [1, 2, 3, 4, 5]
    }).to_csv(path, index=False)

    source = CSVSource(path)

    chunks = list(
        source.iter_chunks("users", chunk_size=2)
    )

    assert len(chunks) == 3
    assert [len(chunk) for chunk in chunks] == [2, 2, 1]
    assert sum(len(chunk) for chunk in chunks) == 5
