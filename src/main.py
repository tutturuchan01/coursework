from src.file_readers import read_excel_file
from src.reports import spending_by_category
from src.services import investment_bank
from src.views import main_page


def main() -> None:
    transactions = read_excel_file("data/operations.xlsx")

    print("Курсовая работа")
    print(f"Загружено операций: {len(transactions)}")

    print("\nИнвестиционная копилка:")
    print(investment_bank("2021-12", transactions, 50))

    print("\nГлавная страница:")
    print(main_page("2021-12-31 23:59:59", transactions))

    print("\nОтчёт по категории:")
    print(
        spending_by_category(
            __import__("pandas").DataFrame(transactions),
            "Супермаркеты",
            "2021-12-31",
        )
    )


if __name__ == "__main__":
    main()
