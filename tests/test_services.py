from src.services import investment_bank


def test_investment_bank():
    transactions = [
        {
            "Дата операции": "2021-12-15 10:00:00",
            "Сумма платежа": -127,
        },
        {
            "Дата операции": "2021-12-20 10:00:00",
            "Сумма платежа": -150,
        },
        {
            "Дата операции": "2021-11-15 10:00:00",
            "Сумма платежа": -200,
        },
        {
            "Дата операции": "2021-12-25 10:00:00",
            "Сумма платежа": 1000,
        },
    ]

    result = investment_bank(
        "2021-12",
        transactions,
        50,
    )

    assert result == 23.0


def test_investment_bank_exact_multiple():
    transactions = [
        {
            "Дата операции": "2021-12-15 10:00:00",
            "Сумма платежа": -100,
        },
    ]

    result = investment_bank(
        "2021-12",
        transactions,
        50,
    )

    assert result == 0.0


def test_investment_bank_different_month():
    transactions = [
        {
            "Дата операции": "2021-11-15 10:00:00",
            "Сумма платежа": -127,
        },
    ]

    result = investment_bank(
        "2021-12",
        transactions,
        50,
    )

    assert result == 0.0
