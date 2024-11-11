import datetime
import math
from typing import Any

from src.logger import setup_logger
from src.utils import read_excel_file

transactions = read_excel_file()

logger = setup_logger("services", "../logs/services")


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """На вход принимаем месяц, транзакции, кратная сумма, до которой округляем.
    Каждая покупка округляется до кратной суммы"""
    month = datetime.datetime.strptime(month, "%Y-%m")
    logger.info(f"Запускаю расчет инвесткопилки для месяца {month.month} с лимитом {limit}")
    sum_investment_bank = 0.0

    for transaction in transactions:
        transaction_date_to_datetime = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")

        if transaction_date_to_datetime.month == month.month and transaction_date_to_datetime.year == month.year:
            payment = transaction["Сумма платежа"]

            if payment < 0 and transaction["Категория"] != "Переводы" and transaction["Категория"] != "Наличные":

                rounded_payment = math.ceil(payment / limit) * limit
                sum_investment_bank += abs(rounded_payment)

    logger.info(f"Расчеты завершены. Сумма накоплений за {month.month} месяц составила бы {sum_investment_bank}")

    return sum_investment_bank