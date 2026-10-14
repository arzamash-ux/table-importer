
import pandas as pd

from .exceptions import DataConversionError


def convert_chunk(
    chunk: pd.DataFrame,
    dtype: dict[str, str] | None = None,
    errors: str = "raise"
) -> pd.DataFrame:
    """
    Преобразует типы столбцов одной части данных.

    Аргументы:
        chunk: Исходный DataFrame.
        dtype: Словарь формата {столбец: тип}.
        errors: Политика обработки ошибок:
                "raise" или "coerce".

    Возвращает:
        Новый DataFrame с преобразованными столбцами.

    Исходный DataFrame не изменяется.
    """
    if errors not in {"raise", "coerce"}:
        raise ValueError(
            "conversion_errors должен быть "
            "'raise' или 'coerce'"
        )

    if not dtype:
        return chunk.copy()

    result = chunk.copy()

    for column, target_type in dtype.items():

        # Проверяем существование указанного столбца.
        if column not in result.columns:
            raise DataConversionError(
                f"Столбец '{column}' не найден. "
                f"Доступные столбцы: {list(result.columns)}"
            )

        try:
            # Отдельно обрабатываем даты.
            if target_type in {
                "datetime64[ns]",
                "datetime"
            }:
                result[column] = pd.to_datetime(
                    result[column],
                    errors=errors
                )

            # Отдельно обрабатываем числовые типы.
            elif target_type in {
                "int64", "Int64",
                "float64", "Float64"
            }:
                numeric = pd.to_numeric(
                    result[column],
                    errors=errors
                )

                # Nullable-типы поддерживают пропуски.
                if errors == "coerce":
                    if target_type in {"int64", "Int64"}:
                        result[column] = numeric.astype("Int64")
                    else:
                        result[column] = numeric.astype("Float64")
                else:
                    result[column] = numeric.astype(target_type)

            # Для остальных типов используем astype.
            else:
                result[column] = result[column].astype(
                    target_type
                )

        except (ValueError, TypeError, OverflowError) as error:
            raise DataConversionError(
                f"Не удалось преобразовать столбец "
                f"'{column}' к типу '{target_type}'. "
                f"Причина: {error}"
            ) from error

    return result
