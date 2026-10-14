
import pandas as pd

from table_importer import TableImporter


def test_session_pause_and_resume(tmp_path):
    """
    Проверяет приостановку и возобновление импорта.
    """
    path = tmp_path / "data.csv"

    expected = pd.DataFrame({
        "id": [1, 2, 3, 4, 5]
    })

    expected.to_csv(path, index=False)

    importer = TableImporter(path)

    session = importer.create_session(
        chunk_size=2
    )

    # Загружаем первую часть.
    first_chunk = session.next_chunk()

    assert len(first_chunk) == 2
    assert session.processed_rows == 2

    # Останавливаем импорт.
    session.pause()

    assert session.is_paused is True
    assert session.next_chunk() is None
    assert session.processed_rows == 2

    # Продолжаем чтение.
    session.resume()

    second_chunk = session.next_chunk()

    assert len(second_chunk) == 2
    assert session.processed_rows == 4

    # Загружаем оставшуюся часть.
    result = session.load_all()

    pd.testing.assert_frame_equal(
        result,
        expected
    )

    assert session.processed_rows == 5
    assert session.is_finished is True


def test_session_load_all(tmp_path):
    """
    Проверяет полную загрузку таблицы через сессию.
    """
    path = tmp_path / "data.csv"

    expected = pd.DataFrame({
        "id": [10, 20, 30, 40]
    })

    expected.to_csv(path, index=False)

    importer = TableImporter(path)
    session = importer.create_session(chunk_size=3)

    result = session.load_all()

    pd.testing.assert_frame_equal(
        result,
        expected
    )

    assert session.processed_rows == 4
    assert session.is_finished is True


def test_session_paused_dataframe(tmp_path):
    """
    Проверяет сохранность данных во время паузы.
    """
    path = tmp_path / "data.csv"

    pd.DataFrame({
        "id": [1, 2, 3, 4]
    }).to_csv(path, index=False)

    importer = TableImporter(path)
    session = importer.create_session(chunk_size=2)

    session.next_chunk()
    session.pause()

    result = session.get_dataframe()

    assert len(result) == 2
    assert result["id"].tolist() == [1, 2]

    # Во время паузы новые данные не читаются.
    session.load_all()

    assert session.processed_rows == 2


def test_session_no_duplicate_rows(tmp_path):
    """
    Проверяет отсутствие повторной загрузки строк
    после нескольких остановок и продолжений.
    """
    path = tmp_path / "data.csv"

    pd.DataFrame({
        "id": list(range(10))
    }).to_csv(path, index=False)

    importer = TableImporter(path)
    session = importer.create_session(chunk_size=3)

    session.next_chunk()

    session.pause()
    session.resume()

    session.next_chunk()

    session.pause()
    session.resume()

    result = session.load_all()

    assert result["id"].tolist() == list(range(10))
    assert session.processed_rows == 10

def test_session_progress(tmp_path):
    """
    Проверяет корректность информации о прогрессе.
    """
    path = tmp_path / "data.csv"

    pd.DataFrame({
        "id": [1, 2, 3, 4, 5]
    }).to_csv(path, index=False)

    importer = TableImporter(path)
    session = importer.create_session(chunk_size=2)

    session.next_chunk()

    assert session.progress["processed_rows"] == 2
    assert session.progress["status"] == "running"

    session.pause()

    assert session.progress["status"] == "paused"

    session.resume()
    session.load_all()

    assert session.progress["processed_rows"] == 5
    assert session.progress["status"] == "finished"
