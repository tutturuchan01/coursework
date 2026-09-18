import pandas as pd


def read_csv_file(file_path: str) -> list[dict]:
    """
    Считывает финансовые операции из CSV-файла.

    :param file_path: путь к CSV-файлу
    :return: список словарей с транзакциями
    """
    df = pd.read_csv(file_path, sep=";")
    return df.to_dict(orient="records")


def read_excel_file(file_path: str) -> list[dict]:
    """
    Считывает финансовые операции из Excel-файла.

    :param file_path: путь к Excel-файлу
    :return: список словарей с транзакциями
    """
    df = pd.read_excel(file_path)
    return df.to_dict(orient="records")
