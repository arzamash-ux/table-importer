
from collections.abc import Iterator
from .converters import convert_chunk
import pandas as pd


class ImportSession:
    """
    Управляет процессом итерационного импорта данных.

    Позволяет:
    - получать данные частями;
    - приостанавливать импорт;
    - возобновлять импорт;
    - отслеживать количество обработанных строк;
    - собирать загруженные данные в один DataFrame.
    """

    def __init__(
        self,
        chunks: Iterator[pd.DataFrame],
        dtype: dict[str, str] | None = None,
        conversion_errors: str = "raise"
    ):
        """
        Создаёт сессию импорта.

        Аргументы:
            chunks: Итератор частей таблицы.
            dtype: Требуемые типы столбцов.
            conversion_errors: Режим обработки ошибок.
        """
        if conversion_errors not in {"raise", "coerce"}:
            raise ValueError(
                "conversion_errors должен быть "
                "'raise' или 'coerce'"
            )

        self._iterator = iter(chunks)

        # Словарь преобразований сохраняется в сессии.
        self._dtype = dtype.copy() if dtype else None
        self._conversion_errors = conversion_errors

        # Накопленные части данных.
        self._chunks = []

        # Количество успешно загруженных строк.
        self._processed_rows = 0

        # Состояние процесса импорта.
        self._paused = False
        self._finished = False
    
    @property
    def processed_rows(self) -> int:
        """
        Возвращает число уже загруженных строк.
        """
        return self._processed_rows

    @property
    def is_paused(self) -> bool:
        """
        Показывает, приостановлена ли сессия.
        """
        return self._paused

    @property
    def is_finished(self) -> bool:
        """
        Показывает, завершена ли загрузка.
        """
        return self._finished

    def pause(self) -> None:
        """
        Приостанавливает импорт данных.

        Ранее загруженные части сохраняются.
        """
        if not self._finished:
            self._paused = True

    def resume(self) -> None:
        """
        Возобновляет импорт после паузы.

        Чтение продолжается с текущего положения
        существующего итератора.
        """
        if not self._finished:
            self._paused = False

    def next_chunk(self) -> pd.DataFrame | None:
        """Получает следующую часть данных и
        преобразует её столбцы к заданным типам.

        Если сессия завершена или приостановлена,
        возвращает None.
        """
        if self._paused or self._finished:
            return None

        try:
            # Получаем следующую часть из источника.
            chunk = next(self._iterator)

        except StopIteration:
            self._finished = True
            return None

        # Преобразуем типы до сохранения чанка.
        converted_chunk = convert_chunk(
            chunk=chunk,
            dtype=self._dtype,
            errors=self._conversion_errors
        )

        # Сохраняем только успешно обработанные данные.
        self._chunks.append(converted_chunk)

        self._processed_rows += len(converted_chunk)

        return converted_chunk
    def load_all(self) -> pd.DataFrame:
        """
        Загружает оставшиеся части таблицы.

        Если сессия находится на паузе,
        возвращает только уже загруженные данные.

        Если сессия активна, продолжает чтение
        до конца источника.
        """
        while not self._paused and not self._finished:
            self.next_chunk()

        return self.get_dataframe()

    def get_dataframe(self) -> pd.DataFrame:
        """
        Объединяет все загруженные части
        в один pandas.DataFrame.

        Не изменяет состояние итератора.
        """
        if not self._chunks:
            return pd.DataFrame()

        return pd.concat(
            self._chunks,
            ignore_index=True
        )
    
    @property
    def progress(self) -> dict:
        """
        Возвращает текущее состояние импорта.

        Количество обработанных строк известно точно.
        Процент не вычисляется, поскольку общее
        число строк источника может быть неизвестно.
        """
        if self._finished:
            status = "finished"
        elif self._paused:
            status = "paused"
        else:
            status = "running"

        return {
            "status": status,
            "processed_rows": self._processed_rows,
            "finished": self._finished
        }
