
class TableImporterError(Exception):
    """
    Базовое исключение библиотеки.

    Позволяет пользователю перехватывать
    все ошибки импорта одним обработчиком.
    """
    pass


class UnsupportedSourceError(TableImporterError):
    """
    Возникает, если формат источника не поддерживается.
    """
    pass


class SourceNotFoundError(TableImporterError):
    """
    Возникает, если исходный файл не найден.
    """
    pass


class TableNotFoundError(TableImporterError):
    """
    Возникает, если запрошенная таблица или лист отсутствует.
    """
    pass


class DataConversionError(TableImporterError):
    """
    Возникает, если значение столбца не удалось
    преобразовать к требуемому типу.
    """
    pass


class SourceReadError(TableImporterError):
    """
    Возникает при ошибке чтения источника данных.
    """
    pass
