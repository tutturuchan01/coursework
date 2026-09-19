import os

import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category():
    transactions = pd.DataFrame(
        [
            {
                "Дата операции": "15.10.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -1000,
            },
            {
                "Дата операции": "20.11.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -500,
            },
            {
                "Дата операции": "10.12.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -300,
            },
            {
                "Дата операции": "10.12.2021 10:00:00",
                "Категория": "Рестораны",
                "Сумма платежа": -700,
            },
        ]
    )

    result = spending_by_category(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 3
    assert result["Сумма платежа"].tolist() == [1000, 500, 300]


def test_spending_by_category_excludes_old_transactions():
    transactions = pd.DataFrame(
        [
            {
                "Дата операции": "15.12.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -1000,
            },
            {
                "Дата операции": "15.08.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -500,
            },
        ]
    )

    result = spending_by_category(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 1
    assert result.iloc[0]["Сумма платежа"] == 1000


def test_spending_by_category_creates_report_file(tmp_path):
    transactions = pd.DataFrame(
        [
            {
                "Дата операции": "15.12.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -1000,
            },
        ]
    )

    current_directory = os.getcwd()

    try:
        os.chdir(tmp_path)

        spending_by_category(
            transactions,
            "Супермаркеты",
            "2021-12-31",
        )

        report_file = tmp_path / "report.txt"

        assert report_file.exists()

    finally:
        os.chdir(current_directory)


def test_save_report_custom_filename(tmp_path):
    transactions = pd.DataFrame(
        [
            {
                "Дата операции": "15.12.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -1000,
            },
        ]
    )

    current_directory = os.getcwd()

    try:
        os.chdir(tmp_path)

        from src.reports import save_report

        @save_report("custom_report.txt")
        def test_report() -> pd.DataFrame:
            return transactions

        test_report()

        report_file = tmp_path / "custom_report.txt"

        assert report_file.exists()

    finally:
        os.chdir(current_directory)
