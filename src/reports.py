import datetime
import os
from functools import wraps
from typing import Any, Callable

import pandas as pd

from src.logger import setup_logger

logger = setup_logger("reports", "../logs/reports")
func_operation_reports = os.path.join(os.path.dirname(__file__), "../data/reports/func_operation.json")
default_path_func_operation_reports = os.path.join(
    os.path.dirname(__file__), "../data/reports/default_func_operation_report.json"
)


def report_write_to_default_file(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        with open(f"{default_path_func_operation_reports}", "w") as file:
            logger.info(
                f"Записываю получившийся результат функции {func.__name__} в файл default_func_operation_report.json"
            )
            result.to_json(file, orient="records", force_ascii=False, indent=4)
        return result

    return wrapper


def report_write_to_file(file_path: str) -> Callable:
    """Записывает в переданный файл результат, который возвращает функция, формирующая отчет."""

    def my_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> pd.DataFrame:
            result = func(*args, **kwargs)
            logger.info(f"Записываю получившийся результат функции {func.__name__} в файл {file_path}")
            result.to_json(file_path, orient="records", force_ascii=False, indent=4)
            return result

        return wrapper

    return my_decorator


@report_write_to_file(func_operation_reports)
def spending_by_category(transactions: pd.DataFrame, category: str, date: Any = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца от переданной даты.

    :param transactions: DataFrame с транзакциями
    :param category: Название категории
    :param date: Опциональная дата в формате "дд.мм.гггг". Если не указана, берется текущая дата
    :return: DataFrame с отфильтрованными данными по категории и дате
    """
    # Если дата не передана, берем текущую дату
    if date is None:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(date, "%d.%m.%Y")
    logger.info(f"Запускаю расчет трат для категории {category} за последние 3 месяца от {date.date()}")
    # Преобразуем столбец "Дата операции" в формат datetime
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Определяем дату 3 месяца назад
    three_months_ago = date - pd.DateOffset(months=3)

    # Фильтруем транзакции по категории и дате
    filtered_transactions = transactions.loc[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= three_months_ago)
        & (transactions["Дата операции"] <= date)
    ]

    # Преобразуем дату обратно в строковый формат
    filtered_transactions = filtered_transactions.assign(
        **{"Дата операции": filtered_transactions["Дата операции"].dt.strftime("%d.%m.%Y %H:%M:%S")}
    )
    logger.info(f"Данные успешно сгенерированы. Количество операций {len(filtered_transactions)}")
    return filtered_transactions