import json
from datetime import datetime
from typing import Any, cast

import pandas as pd
import requests


def get_greeting(date_string: str) -> str:
    """Возвращает приветствие в зависимости от времени суток."""

    date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    hour = date.hour

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_cards_info(
    transactions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Формирует информацию о картах.

    :param transactions: список банковских операций
    :return: информация по каждой карте
    """

    cards: dict[str, float] = {}

    for transaction in transactions:
        card_number = transaction.get("Номер карты")

        if pd.isna(card_number):
            continue

        last_four_digits = str(card_number)[-4:]

        if last_four_digits not in cards:
            cards[last_four_digits] = 0.0

        amount = transaction.get("Сумма платежа", 0)

        if isinstance(amount, (int, float)) and amount < 0:
            cards[last_four_digits] += abs(float(amount))

    return [
        {
            "last_digits": last_four_digits,
            "total_spent": round(total_spent, 2),
            "cashback": round(total_spent / 100, 2),
        }
        for last_four_digits, total_spent in cards.items()
    ]


def get_top_transactions(
    transactions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Возвращает 5 крупнейших операций по сумме платежа.

    :param transactions: список банковских операций
    :return: список из 5 крупнейших операций
    """

    sorted_transactions = sorted(
        transactions,
        key=lambda transaction: float(
            transaction.get("Сумма платежа", 0)
        ),
        reverse=True,
    )

    top_transactions = []

    for transaction in sorted_transactions[:5]:
        date = transaction.get("Дата операции", "")

        if isinstance(date, datetime):
            formatted_date = date.strftime("%d.%m.%Y")
        else:
            formatted_date = str(date)[:10]

        top_transactions.append(
            {
                "date": formatted_date,
                "amount": float(
                    transaction.get("Сумма платежа", 0)
                ),
                "category": transaction.get("Категория", ""),
                "description": transaction.get("Описание", ""),
            }
        )

    return top_transactions


def filter_transactions_by_date(
    transactions: list[dict[str, Any]],
    date_string: str,
) -> list[dict[str, Any]]:
    """
    Оставляет операции с начала месяца до указанной даты включительно.

    :param transactions: список банковских операций
    :param date_string: дата в формате YYYY-MM-DD HH:MM:SS
    :return: отфильтрованные операции
    """

    end_date = datetime.strptime(
        date_string,
        "%Y-%m-%d %H:%M:%S",
    )

    start_date = end_date.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
    )

    filtered_transactions = []

    for transaction in transactions:
        operation_date = transaction.get("Дата операции")

        if pd.isna(operation_date):
            continue

        if not isinstance(operation_date, datetime):
            operation_date = pd.to_datetime(
                operation_date,
                format="%d.%m.%Y %H:%M:%S",
            )

        if start_date <= operation_date <= end_date:
            filtered_transactions.append(transaction)

    return filtered_transactions


def get_expenses(
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Формирует информацию о расходах.

    В основные категории попадают 7 категорий
    с наибольшими расходами. Остальные категории
    объединяются в категорию «Остальное».

    Переводы и наличные выделяются отдельно.

    :param transactions: список банковских операций
    :return: информация о расходах
    """

    expenses_by_category: dict[str, float] = {}

    for transaction in transactions:
        amount = transaction.get("Сумма платежа", 0)
        category = transaction.get("Категория", "")

        if not isinstance(amount, (int, float)):
            continue

        if amount >= 0:
            continue

        if not category:
            continue

        amount = abs(float(amount))
        expenses_by_category[category] = (
            expenses_by_category.get(category, 0.0) + amount
        )

    total_amount = sum(expenses_by_category.values())

    special_categories = {"Переводы", "Наличные"}

    transfers_and_cash = [
        {
            "category": category,
            "amount": round(expenses_by_category[category]),
        }
        for category in special_categories
        if category in expenses_by_category
    ]

    transfers_and_cash.sort(
        key=lambda item: cast(int, item["amount"]),
        reverse=True,
    )

    regular_categories = {
        category: amount
        for category, amount in expenses_by_category.items()
        if category not in special_categories
    }

    sorted_categories = sorted(
        regular_categories.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_categories = [
        {
            "category": category,
            "amount": round(amount),
        }
        for category, amount in sorted_categories[:7]
    ]

    other_amount = sum(
        amount for _, amount in sorted_categories[7:]
    )

    if other_amount > 0:
        main_categories.append(
            {
                "category": "Остальное",
                "amount": round(other_amount),
            }
        )

    return {
        "total_amount": round(total_amount),
        "main": main_categories,
        "transfers_and_cash": transfers_and_cash,
    }


def get_income(
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Формирует информацию о поступлениях.

    Поступления группируются по категориям
    и сортируются по убыванию суммы.

    :param transactions: список банковских операций
    :return: информация о поступлениях
    """

    income_by_category: dict[str, float] = {}

    for transaction in transactions:
        amount = transaction.get("Сумма платежа", 0)
        category = transaction.get("Категория", "")

        if not isinstance(amount, (int, float)):
            continue

        if amount <= 0:
            continue

        if not category:
            continue

        amount = float(amount)

        income_by_category[category] = (
            income_by_category.get(category, 0.0) + amount
        )

    total_amount = sum(income_by_category.values())

    sorted_categories = sorted(
        income_by_category.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_categories = [
        {
            "category": category,
            "amount": round(amount),
        }
        for category, amount in sorted_categories
    ]

    return {
        "total_amount": round(total_amount),
        "main": main_categories,
    }


def main_page(
    date_string: str,
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Формирует основную информацию для главной страницы.

    :param date_string: дата в формате YYYY-MM-DD HH:MM:SS
    :param transactions: список банковских операций
    :return: данные для главной страницы
    """

    filtered_transactions = filter_transactions_by_date(
        transactions,
        date_string,
    )

    settings = load_user_settings()

    result = {
        "greeting": get_greeting(date_string),
        "cards": get_cards_info(filtered_transactions),
        "expenses": get_expenses(filtered_transactions),
        "income": get_income(filtered_transactions),
        "top_transactions": get_top_transactions(
            filtered_transactions
        ),
        "currency_rates": get_currency_rates(
            settings["user_currencies"]
        ),
        "stock_prices": get_stock_prices(
            settings["user_stocks"]
        ),
    }

    return result


def load_user_settings(
    file_path: str = "user_settings.json",
) -> dict[str, Any]:
    """
    Загружает настройки пользователя из JSON-файла.

    :param file_path: путь к файлу настроек
    :return: настройки пользователя
    """

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return cast(dict[str, Any], data)


def get_currency_rates(
    currencies: list[str],
) -> list[dict[str, Any]]:
    """
    Получает актуальные курсы валют.

    :param currencies: список валют из настроек пользователя
    :return: список курсов валют
    """

    response = requests.get(
        "https://api.frankfurter.dev/v2/rates",
        params={
            "base": "RUB",
            "quotes": ",".join(currencies),
        },
    )

    try:
        response.raise_for_status()
        rates = response.json()
    except requests.RequestException:
        return []

    return [
        {
            "currency": rate["quote"],
            "rate": float(rate["rate"]),
        }
        for rate in rates
    ]


def get_stock_prices(
    stocks: list[str],
) -> list[dict[str, Any]]:
    """
    Получает текущие цены акций.

    :param stocks: список тикеров из настроек пользователя
    :return: список цен акций
    """

    stock_prices = []

    for stock in stocks:
        response = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}",
            params={
                "range": "1d",
                "interval": "1d",
            },
            headers={
                "User-Agent": "Mozilla/5.0",
            },
            timeout=10,
        )

        try:
            response.raise_for_status()
            data = response.json()
            result = data["chart"]["result"][0]
            price = result["meta"]["regularMarketPrice"]
        except (
            requests.RequestException,
            KeyError,
            TypeError,
            IndexError,
        ):
            continue

        stock_prices.append(
            {
                "stock": stock,
                "price": float(price),
            }
        )

    return stock_prices
