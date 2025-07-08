import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.services import get_transaction_history, service_cashback


def test_get_transaction_history_basic(sample_transaction_data_cashback):
    """Проверка базовой функциональности - возврат транзакций за указанный месяц"""
    result = get_transaction_history(sample_transaction_data_cashback, 2023, "5")

    assert len(result) == 3
    assert all(op["Описание"] in [f"Транзакция {i}" for i in [1, 2, 3]] for op in result)


def test_get_transaction_history_boundary_dates(sample_transaction_data_cashback):
    """Проверка включения граничных дат (первое и последнее число месяца)"""
    result = get_transaction_history(sample_transaction_data_cashback, 2023, "5")

    dates = [op["Дата операции"] for op in result]
    assert datetime(2023, 5, 1) in dates
    assert datetime(2023, 5, 31) in dates


def test_get_transaction_history_exclusion(sample_transaction_data_cashback):
    """Проверка исключения транзакций за другие месяцы"""
    result = get_transaction_history(sample_transaction_data_cashback, 2023, "5")

    dates = [op["Дата операции"] for op in result]
    assert datetime(2023, 4, 30) not in dates
    assert datetime(2023, 6, 1) not in dates
    assert datetime(2022, 5, 15) not in dates


def test_get_transaction_history_leap_year():
    """Проверка обработки февраля в високосном году"""
    # Создаем данные с февральскими транзакциями
    data = [
        {"Дата операции": datetime(2020, 2, 28), "Описание": "День 28"},
        {"Дата операции": datetime(2020, 2, 29), "Описание": "День 29"},
        {"Дата операции": datetime(2020, 3, 1), "Описание": "День 1"},
    ]
    df = pd.DataFrame(data)

    result = get_transaction_history(df, 2020, "2")

    assert len(result) == 2
    assert any(op["Описание"] == "День 29" for op in result)
    assert not any(op["Описание"] == "День 1" for op in result)


def test_get_transaction_history_non_leap_year():
    """Проверка обработки февраля в невисокосном году"""
    data = [
        {"Дата операции": datetime(2023, 2, 28), "Описание": "День 28"},
        {"Дата операции": datetime(2023, 3, 1), "Описание": "День 1"},
    ]
    df = pd.DataFrame(data)

    result = get_transaction_history(df, 2023, "2")

    assert len(result) == 1
    assert result[0]["Описание"] == "День 28"


def test_service_cashback_basic(sample_transactions_cashback_info):
    """Проверка базовой функциональности"""
    year = 2023
    month = "5"
    # Передаем DataFrame в функцию
    result = service_cashback(sample_transactions_cashback_info, year, month)
    result_dict = json.loads(result)

    # Проверяем результаты
    assert result_dict == {
        "Продукты": 70,  # 50 + 20 (только за май)
        "Транспорт": 30
    }


def test_service_cashback_excluded_categories(sample_transactions_cashback_info):
    """Проверка игнорирования исключенных категорий"""
    year = 2023
    month = "5"
    result = service_cashback(sample_transactions_cashback_info, year, month)
    result_dict = json.loads(result)

    assert result_dict == {
        "Продукты": 70,
        "Транспорт": 30,
    }


def test_service_cashback_sorting(sample_transactions_cashback_info):
    """Проверка сортировки по убыванию кэшбэка"""
    # Создаем копию DataFrame, чтобы не изменять оригинальную фикстуру
    df = sample_transactions_cashback_info.copy()

    # Добавляем новую транзакцию
    new_transaction = pd.DataFrame([{
        "Дата операции": datetime(2023, 5, 15),
        "Категория": "Рестораны",
        "Бонусы (включая кэшбэк)": 100
    }])
    df = pd.concat([df, new_transaction], ignore_index=True)

    year = 2023
    month = "5"
    result = service_cashback(df, year, month)
    result_dict = json.loads(result)

    # Проверяем порядок ключей
    keys = list(result_dict.keys())
    assert keys == ["Рестораны", "Продукты", "Транспорт"]
    assert result_dict == {
        "Рестораны": 100,
        "Продукты": 70,
        "Транспорт": 30
    }


@patch('src.services.get_transaction_history')
@patch('src.services.get_categories')
def test_service_cashback_empty_month(mock_get_categories, mock_get_history, sample_transactions_cashback_info):
    """Проверка обработки месяца без транзакций"""
    mock_get_history.return_value = []
    mock_get_categories.return_value = []

    year = 2023
    month = "6"  # Месяц без данных
    result = service_cashback(sample_transactions_cashback_info, year, month)
    result_dict = json.loads(result)

    assert result_dict == {}


@patch('src.services.get_transaction_history')
@patch('src.services.get_categories')
def test_service_cashback_zero_cashback(mock_get_categories, mock_get_history, sample_transactions_cashback_info):
    """Проверка обработки нулевого кэшбэка"""
    # Создаем модифицированный DataFrame с нулевыми бонусами
    df = sample_transactions_cashback_info.copy()
    df["Бонусы (включая кэшбэк)"] = 0

    mock_get_history.return_value = df.to_dict("records")
    mock_get_categories.return_value = ["Продукты", "Транспорт", "Наличные", "Переводы"]

    year = 2023
    month = "5"
    result = service_cashback(df, year, month)
    result_dict = json.loads(result)

    assert result_dict == {
        "Продукты": 0,
        "Транспорт": 0,
        "Наличные": 0,
        "Переводы": 0
    }