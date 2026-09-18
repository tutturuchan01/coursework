from datetime import datetime
from typing import Any


def investment_bank(
    month: str,
    transactions: list[dict[str, Any]],
    limit: int,
) -> float:
    """
    Рассчитывает сумму, которую можно отложить
    в инвестиционную копилку за указанный месяц.

    :param month: месяц в формате YYYY-MM
    :param transactions: список банковских операций
    :param limit: сумма округления
    :return: сумма, отложенная в инвестиционную копилку
    """

    def is_valid_transaction(transaction: dict[str, Any]) -> bool:
        date = transaction.get("Дата операции", "")
        amount = transaction.get(
            "Сумма операции",
            transaction.get("Сумма платежа", 0),
        )

        if not date or not isinstance(amount, (int, float)):
            return False

        date_string = str(date)

        if "." in date_string[:10]:
            try:
                transaction_date = datetime.strptime(
                    date_string[:10],
                    "%d.%m.%Y",
                )
                transaction_month = transaction_date.strftime("%Y-%m")
            except ValueError:
                return False
        else:
            transaction_month = date_string[:7]

        return (
            transaction_month == month
            and amount < 0
        )

    valid_transactions = filter(
        is_valid_transaction,
        transactions,
    )

    def get_round_up(transaction: dict[str, Any]) -> float:
        amount = transaction.get(
            "Сумма операции",
            transaction.get("Сумма платежа", 0),
        )

        amount = abs(float(amount))
        remainder = amount % limit

        if remainder == 0:
            return 0.0

        return limit - remainder

    round_ups = map(
        get_round_up,
        valid_transactions,
    )

    return round(sum(round_ups), 2)
