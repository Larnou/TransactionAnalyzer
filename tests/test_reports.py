from datetime import datetime, timedelta

import pandas as pd

from src.reports import log, spending_by_category


def successful_function(a, b):
    return a + b


def failing_function():
    raise ValueError("Test error")


def test_log_success_file(tmp_path):
    log_file = tmp_path / "test.log"

    @log(filename=str(log_file))
    def test_func(a, b, c=10):
        return a + b + c

    result = test_func(5, 7, c=3)
    content = log_file.read_text()

    assert result == 15
    assert "Function name: test_func()" in content
    assert "The result of the function execution test_func(): 15" in content

# def test_log_success_file_no_filename(tmp_path):
#     log_file = tmp_path / "test_func.log"
#
#     @log()
#     def test_func(a, b, c=10):
#         return a + b + c
#
#     result = test_func(5, 7, c=3)
#     content = log_file.read_text()
#
#     assert result == 15
#     assert "Function name: test_func()" in content
#     assert "The result of the function execution test_func(): 15" in content


def test_log_exception_file(tmp_path):
    log_file = tmp_path / "error.log"

    @log(filename=str(log_file))
    def test_division_func(a, b=0):
        return a / b

    result = test_division_func(10, 0)
    content = log_file.read_text()

    assert result is None
    assert "Function name: test_division_func()" in content
    assert "division by zero" in content
    assert "Arguments used: (0,) and {}" in content


def test_spending_by_category():
    """Проверка фильтрации по категории и временному диапазону"""
    data = {
        "Дата операции": [
            datetime(2025, 4, 20),  # До периода
            datetime(2025, 4, 21),  # Начало периода
            datetime(2025, 7, 22),  # Конец периода
            datetime(2025, 7, 23),  # После периода
        ],
        "Категория": ["food", "food", "food", "tech"],
        "Сумма": [100, 200, 300, 400]
    }
    transactions = pd.DataFrame(data)
    date = "22.07.2025 00:00:00"

    result = spending_by_category(transactions, "food", date)

    # Проверяем количество строк и значения
    assert len(result) == 2
    assert result["Сумма"].tolist() == [200, 300]
    assert result["Дата операции"].min() == datetime(2025, 4, 21)
    assert result["Дата операции"].max() == datetime(2025, 7, 22)


def test_spending_by_category_empty_result():
    """Проверка пустого результата при отсутствии подходящих транзакций"""
    data = {
        "Дата операции": [datetime(2025, 7, 22)],
        "Категория": ["tech"],
        "Сумма": [500]
    }
    transactions = pd.DataFrame(data)

    result = spending_by_category(transactions, "food", "22.07.2025 00:00:00")

    assert result.empty


def test_spending_by_category_boundary_dates():
    """Проверка корректности включения граничных дат"""
    start_date = datetime(2025, 4, 21)
    end_date = datetime(2025, 7, 22)
    data = {
        "Дата операции": [start_date - timedelta(minutes=1), start_date, end_date, end_date + timedelta(minutes=1)],
        "Категория": ["food"] * 4,
        "Сумма": [1, 2, 3, 4]
    }
    transactions = pd.DataFrame(data)
    date = "22.07.2025 00:00:00"

    result = spending_by_category(transactions, "food", date)

    assert len(result) == 2
    assert result["Сумма"].tolist() == [2, 3]