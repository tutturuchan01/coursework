from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd


def save_report(
    filename: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для сохранения результата отчета в файл.

    Если имя файла не передано, используется имя report.txt.
    """

    def decorator(
        func: Callable[..., Any],
    ) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            result = func(*args, **kwargs)

            output_filename = filename or "report.txt"

            if isinstance(result, pd.DataFrame):
                result.to_json(
                    output_filename,
                    orient="records",
                    force_ascii=False,
                    indent=4,
                    date_format="iso",
                )
            else:
                with open(
                    output_filename,
                    "w",
                    encoding="utf-8",
                ) as file:
                    file.write(str(result))

            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории
    за последние три месяца.

    :param transactions: датафрейм с транзакциями
    :param category: название категории
    :param date: дата в формате YYYY-MM-DD
    :return: датафрейм с тратами по категории
    """

    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(
            date,
            "%Y-%m-%d",
        )

    start_date = end_date - pd.DateOffset(months=3)

    data = transactions.copy()

    data["Дата операции"] = pd.to_datetime(
        data["Дата операции"],
        dayfirst=True,
    )

    filtered = data[
        (data["Дата операции"] >= start_date)
        & (data["Дата операции"] <= end_date)
        & (data["Категория"] == category)
        & (data["Сумма платежа"] < 0)
    ].copy()

    filtered["Сумма платежа"] = filtered["Сумма платежа"].abs()

    return filtered
