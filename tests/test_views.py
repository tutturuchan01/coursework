from datetime import datetime

from src.views import (
    filter_transactions_by_date,
    get_cards_info,
    get_greeting,
    get_top_transactions,
    load_user_settings,
)


def test_get_greeting():
    assert get_greeting("2021-12-31 08:00:00") == "Доброе утро"
    assert get_greeting("2021-12-31 14:00:00") == "Добрый день"
    assert get_greeting("2021-12-31 20:00:00") == "Добрый вечер"
    assert get_greeting("2021-12-31 02:00:00") == "Доброй ночи"


def test_get_cards_info():
    transactions = [
        {
            "Номер карты": "*7197",
            "Сумма платежа": -1000.0,
        },
        {
            "Номер карты": "*7197",
            "Сумма платежа": -500.0,
        },
        {
            "Номер карты": "*5091",
            "Сумма платежа": -2000.0,
        },
        {
            "Номер карты": "*7197",
            "Сумма платежа": 3000.0,
        },
    ]

    result = get_cards_info(transactions)

    assert result == [
        {
            "last_digits": "7197",
            "total_spent": 1500.0,
            "cashback": 15.0,
        },
        {
            "last_digits": "5091",
            "total_spent": 2000.0,
            "cashback": 20.0,
        },
    ]


def test_get_top_transactions():
    transactions = [
        {
            "Дата операции": "01.12.2021 10:00:00",
            "Сумма платежа": 100.0,
            "Категория": "Продукты",
            "Описание": "Магазин",
        },
        {
            "Дата операции": "02.12.2021 10:00:00",
            "Сумма платежа": 500.0,
            "Категория": "Переводы",
            "Описание": "Перевод",
        },
        {
            "Дата операции": "03.12.2021 10:00:00",
            "Сумма платежа": -300.0,
            "Категория": "Супермаркеты",
            "Описание": "Покупка",
        },
        {
            "Дата операции": "04.12.2021 10:00:00",
            "Сумма платежа": 1000.0,
            "Категория": "Пополнения",
            "Описание": "Пополнение",
        },
    ]

    result = get_top_transactions(transactions)

    assert result == [
        {
            "date": "04.12.2021",
            "amount": 1000.0,
            "category": "Пополнения",
            "description": "Пополнение",
        },
        {
            "date": "02.12.2021",
            "amount": 500.0,
            "category": "Переводы",
            "description": "Перевод",
        },
        {
            "date": "01.12.2021",
            "amount": 100.0,
            "category": "Продукты",
            "description": "Магазин",
        },
        {
            "date": "03.12.2021",
            "amount": -300.0,
            "category": "Супермаркеты",
            "description": "Покупка",
        },
    ]


def test_filter_transactions_by_date():
    transactions = [
        {
            "Дата операции": datetime(2021, 12, 1, 10, 0, 0),
            "Номер карты": "*7197",
            "Сумма платежа": -100.0,
        },
        {
            "Дата операции": datetime(2021, 12, 15, 10, 0, 0),
            "Номер карты": "*7197",
            "Сумма платежа": -200.0,
        },
        {
            "Дата операции": datetime(2021, 12, 31, 23, 59, 59),
            "Номер карты": "*7197",
            "Сумма платежа": -300.0,
        },
        {
            "Дата операции": datetime(2021, 11, 30, 10, 0, 0),
            "Номер карты": "*7197",
            "Сумма платежа": -400.0,
        },
    ]

    result = filter_transactions_by_date(
        transactions,
        "2021-12-31 23:59:59",
    )

    assert len(result) == 3
    assert result[0]["Сумма платежа"] == -100.0
    assert result[-1]["Сумма платежа"] == -300.0


def test_load_user_settings(tmp_path):
    settings_file = tmp_path / "user_settings.json"

    settings_file.write_text(
        '{"user_currencies": ["USD", "EUR"], '
        '"user_stocks": ["AAPL", "MSFT"]}',
        encoding="utf-8",
    )

    result = load_user_settings(str(settings_file))

    assert result == {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "MSFT"],
    }
