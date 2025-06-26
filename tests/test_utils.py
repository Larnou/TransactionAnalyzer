import json
import math
from datetime import datetime
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.utils import get_welcome_words, get_transaction_history, get_card_numbers, get_transactions_by_card_number, \
    get_card_transactions_info, get_top_transactions


# Параметризованный тест для всех случаев
@pytest.mark.parametrize("hour, minute, expected", [
    (0, 0, "Доброй ночи"),  # Полночь
    (5, 59, "Доброй ночи"),  # Почти утро
    (6, 0, "Доброе утро"),  # Ровно 6 утра
    (11, 59, "Доброе утро"),  # Почти полдень
    (12, 0, "Добрый день"),  # Полдень
    (17, 59, "Добрый день"),  # Почти вечер
    (18, 0, "Добрый вечер"),  # Ровно 6 вечера
    (23, 59, "Добрый вечер")  # Почти полночь
])
def test_get_welcome_words(hour, minute, expected, monkeypatch):
    # Создаем фейковый datetime
    class MockDateTime:
        @classmethod
        def now(cls):
            return datetime(2023, 1, 1, hour, minute)

    # Подменяем datetime в модуле с функцией
    monkeypatch.setattr("src.utils.datetime", MockDateTime)

    assert get_welcome_words() == expected


def test_get_transaction_history_standard_period(sample_transactions):
    """
    Стандартный случай: период 01.05.2023 - 20.05.2023 23:59:59
    """
    result = get_transaction_history(
        transaction_data=sample_transactions,
        period_end="20.05.2023 23:59:59"
    )

    # Должны попасть первые 3 транзакции
    assert len(result) == 3
    assert {t["Дата операции"] for t in result} == {
        datetime(2023, 5, 1, 0, 0, 0),
        datetime(2023, 5, 15, 12, 30, 0),
        datetime(2023, 5, 20, 23, 59, 59)
    }


def test_get_transaction_history_start_of_month_boundary(sample_transactions):
    """
    Граничный случай: период заканчивается в начале месяца
    """
    result = get_transaction_history(
        transaction_data=sample_transactions,
        period_end="01.05.2023 00:00:01"
    )

    # Только первая транзакция
    assert len(result) == 1
    assert result[0]["Дата операции"] == datetime(2023, 5, 1, 0, 0, 0)


def test_get_transaction_history_end_of_month(sample_transactions):
    """
    Период до конца месяца
    """
    result = get_transaction_history(
        transaction_data=sample_transactions,
        period_end="31.05.2023 23:59:59"
    )

    # Все майские транзакции (первые 4)
    assert len(result) == 4
    assert result[3]["Дата операции"] == datetime(2023, 5, 21, 0, 0, 0)


def test_get_transaction_history_empty_result(sample_transactions):
    """
    Нет транзакций в указанном периоде
    """
    # Период в будущем
    result = get_transaction_history(
        transaction_data=sample_transactions,
        period_end="01.04.2023 00:00:00"
    )
    assert len(result) == 0

    # Период в прошлом
    result = get_transaction_history(
        transaction_data=sample_transactions,
        period_end="01.07.2023 00:00:00"
    )
    # Не должно включать транзакции июня
    assert len(result) == 0


def test_get_transaction_history_datetime_boundaries(sample_transactions):
    """
    Проверка точных временных границ
    """
    # Граница на миллисекунду раньше
    result = get_transaction_history(
        transaction_data=sample_transactions,
        period_end="20.05.2023 23:59:58"
    )
    dates = {t["Дата операции"] for t in result}
    assert datetime(2023, 5, 20, 23, 59, 59) not in dates

    # Граница ровно в конечное время
    result = get_transaction_history(
        transaction_data=sample_transactions,
        period_end="20.05.2023 23:59:59"
    )
    dates = {t["Дата операции"] for t in result}
    assert datetime(2023, 5, 20, 23, 59, 59) in dates


def test_get_transaction_history_leap_year():
    """
    Проверка корректной работы с високосным годом
    """
    transactions = pd.DataFrame({
        "Дата операции": [datetime(2024, 2, 29, 12, 0, 0)]
    })

    result = get_transaction_history(
        transaction_data=transactions,
        period_end="29.02.2024 23:59:59"
    )

    assert len(result) == 1
    assert result[0]["Дата операции"] == datetime(2024, 2, 29, 12, 0, 0)


def test_get_card_numbers_basic_functionality(sample_card_numbers):
    """Тест базовой функциональности: уникальные номера карт"""

    result = get_card_numbers(sample_card_numbers)
    assert result == {"1234567812345678", "8765432187654321"}


def test_get_card_numbers_nan_values():
    """Тест фильтрации NaN значений"""
    transactions = [
        {"Номер карты": "1111222233334444"},
        {"Номер карты": float('nan')},
        {"Номер карты": math.nan},
        {"Номер карты": np.nan},
        {"Номер карты": "5555666677778888"},
    ]

    result = get_card_numbers(transactions)
    assert result == {"1111222233334444", "5555666677778888"}


def test_get_card_numbers_empty_input():
    """Тест пустого ввода"""
    assert get_card_numbers([]) == set()


def test_get_card_numbers_missing_card_field():
    """Тест отсутствия поля 'Номер карты' в некоторых транзакциях"""
    transactions = [
        {"Номер карты": "1234123412341234"},
        {"Другой ключ": "значение"},  # Нет номера карты
        {"Номер карты": None},
        {},  # Пустой словарь
        {"Номер карты": "5678567856785678"},
    ]

    result = get_card_numbers(transactions)
    assert result == {"1234123412341234", "5678567856785678", None}


def test_get_card_numbers_mixed_types():
    """Тест обработки разных типов данных"""
    transactions = [
        {"Номер карты": 1234567812345678},  # Число
        {"Номер карты": "1234567812345678"},  # Строка
        {"Номер карты": True},  # Булево значение
        {"Номер карты": None},
        {"Номер карты": float('nan')},
    ]

    result = get_card_numbers(transactions)
    assert result == {1234567812345678, "1234567812345678", True, None}


def test_get_card_numbers_none_handling():
    """Тест обработки None значений"""
    transactions = [
        {"Номер карты": None},
        {"Номер карты": "None"},  # Строка "None"
        {"Номер карты": "0000000000000000"},
        {"Номер карты": None},  # Дубликат None
    ]

    result = get_card_numbers(transactions)
    assert result == {None, "None", "0000000000000000"}


def test_get_card_numbers_all_nan():
    """Тест случая, когда все значения NaN"""
    transactions = [
        {"Номер карты": float('nan')},
        {"Номер карты": np.nan},
        {"Номер карты": math.nan},
    ]

    result = get_card_numbers(transactions)
    assert result == set()


def test_get_card_numbers_special_cases():
    """Тест специальных случаев"""
    transactions = [
        {"Номер карты": ""},  # Пустая строка
        {"Номер карты": " "},  # Пробел
        {"Номер карты": 0},  # Ноль
        {"Номер карты": False},  # False
        {"Номер карты": float('nan')},
    ]

    result = get_card_numbers(transactions)
    assert result == {"", " ", 0, False}


def test_get_transactions_by_card_number_basic_filtering(sample_transactions_for_card_numbers):
    """Тест базовой фильтрации по существующему номеру карты"""
    result = get_transactions_by_card_number(
        transaction_data=sample_transactions_for_card_numbers,
        card_number="1234567812345678"
    )

    assert len(result) == 3
    assert all(t["Номер карты"] == "1234567812345678" for t in result)
    assert {t["Сумма"] for t in result} == {700, 100, 300}


def test_get_transactions_by_card_number_no_matching_card(sample_transactions_for_card_numbers):
    """Тест отсутствия транзакций для заданного номера карты"""
    result = get_transactions_by_card_number(
        transaction_data=sample_transactions_for_card_numbers,
        card_number="9999999999999999"
    )
    assert result == []


def test_get_transactions_by_card_number_filtering_none_value(sample_transactions_for_card_numbers):
    """Тест фильтрации по None значению"""
    result = get_transactions_by_card_number(
        transaction_data=sample_transactions_for_card_numbers,
        card_number=None
    )
    assert len(result) == 1
    assert result[0]["Сумма"] == 400


def test_get_transactions_by_card_number_filtering_nan_value(sample_transactions_for_card_numbers):
    """Тест фильтрации по NaN значению (особое поведение)"""
    # Важно: NaN != NaN, поэтому напрямую не сработает
    result = get_transactions_by_card_number(
        transaction_data=sample_transactions_for_card_numbers,
        card_number=math.nan
    )
    assert len(result) == 0  # Потому что math.nan != math.nan


def test_get_transactions_by_card_number_empty_transaction_list():
    """Тест пустого списка транзакций"""
    assert get_transactions_by_card_number([], "1234567812345678") == []


def test_get_transactions_by_card_number_missing_card_key(sample_transactions_for_card_numbers):
    """Тест обработки транзакций без поля 'Номер карты'"""
    result = get_transactions_by_card_number(
        transaction_data=sample_transactions_for_card_numbers,
        card_number="8765432187654321"
    )
    assert len(result) == 1
    assert result[0]["Сумма"] == 200


def test_get_transactions_by_card_number_special_characters_in_card():
    """Тест фильтрации по номеру со спецсимволами"""
    transactions = [
        {"Номер карты": "1234****5678", "Сумма": 100},
        {"Номер карты": "1234****5678", "Сумма": 200},
        {"Номер карты": "1111****2222", "Сумма": 300},
    ]

    result = get_transactions_by_card_number(
        transaction_data=transactions,
        card_number="1234****5678"
    )
    assert len(result) == 2
    assert {t["Сумма"] for t in result} == {100, 200}


def test_get_transactions_by_card_number_case_sensitivity():
    """Тест чувствительности к регистру"""
    transactions = [
        {"Номер карты": "AaBbCcDd", "Сумма": 100},
        {"Номер карты": "aabbccdd", "Сумма": 200},
    ]

    result = get_transactions_by_card_number(
        transaction_data=transactions,
        card_number="AaBbCcDd"
    )
    assert len(result) == 1
    assert result[0]["Сумма"] == 100


def test_get_transactions_by_card_number_different_data_types():
    """Тест разных типов данных в номере карты"""
    transactions = [
        {"Номер карты": 12345678, "Сумма": 100},  # Число
        {"Номер карты": "12345678", "Сумма": 200},  # Строка
        {"Номер карты": True, "Сумма": 300},  # Булево значение
    ]


    # Тест для числа
    result = get_transactions_by_card_number(transactions, 12345678)
    assert len(result) == 1
    assert result[0]["Сумма"] == 100

    # Тест для строки
    result = get_transactions_by_card_number(transactions, "12345678")
    assert len(result) == 1
    assert result[0]["Сумма"] == 200

    # Тест для булева значения
    result = get_transactions_by_card_number(transactions, True)
    assert len(result) == 1
    assert result[0]["Сумма"] == 300


def test_get_transactions_by_card_number_partial_match():
    """Тест на частичное совпадение (должно быть полное совпадение)"""
    transactions = [
        {"Номер карты": "12345678", "Сумма": 100},
        {"Номер карты": "123456789", "Сумма": 200},
    ]

    result = get_transactions_by_card_number(transactions, "12345678")
    assert len(result) == 1
    assert result[0]["Сумма"] == 100


def test_get_card_transactions_info_basic_calculation(sample_transactions_cashback):
    """Тест базового расчета трат и кешбека"""
    result = get_card_transactions_info(
        card_transactions=sample_transactions_cashback,
        card_number="1234"
    )

    # Ожидаемые траты: 100 + 200.50 + 0.01 + 150 = 450.51
    # Кешбек: 450.51 / 100 = 4.5051 → округляем до 4.51
    assert result["last_digits"] == "1234"
    assert result["total_spent"] == 450.51
    assert result["cashback"] == 4.51


def test_get_card_transactions_info_empty_transactions():
    """Тест пустого списка транзакций"""
    result = get_card_transactions_info([], "5678")
    assert result == {
        "last_digits": "5678",
        "total_spent": 0.0,
        "cashback": 0.0
    }


def test_get_card_transactions_info_only_positive_operations():
    """Тест только положительных операций (пополнений)"""
    transactions = [
        {"Сумма операции": 100.0},
        {"Сумма операции": 200.0},
        {"Сумма операции": 300.0},
    ]

    result = get_card_transactions_info(transactions, "9999")
    assert result["total_spent"] == 0.0
    assert result["cashback"] == 0.0


def test_get_card_transactions_info_nan_handling():
    """Тест обработки NaN значений"""
    transactions = [
        {"Сумма операции": math.nan},
        {"Сумма операции": np.nan},
        {"Сумма операции": -100.0},
    ]

    result = get_card_transactions_info(transactions, "0000")
    assert result["total_spent"] == 100.0
    assert result["cashback"] == 1.0


def test_get_card_transactions_info_rounding():
    """Тест округления сумм"""
    transactions = [
        {"Сумма операции": -100.004},  # Должно округлиться до 100.00
        {"Сумма операции": -100.005},  # Должно округлиться до 100.01
        {"Сумма операции": -33.333},
        {"Сумма операции": -66.666},
    ]

    result = get_card_transactions_info(transactions, "2222")
    assert result["total_spent"] == pytest.approx(300.00, 0.01)
    assert result["cashback"] == pytest.approx(3.00, 0.01)


def test_get_card_transactions_info_large_numbers():
    """Тест больших сумм"""
    transactions = [
        {"Сумма операции": -1_000_000.0},
        {"Сумма операции": -2_500_000.0},
    ]

    result = get_card_transactions_info(transactions, "3333")
    assert result["total_spent"] == 3_500_000.0
    assert result["cashback"] == 35_000.0


def test_get_card_transactions_info_mixed_currencies():
    """Тест разных форматов сумм"""
    transactions = [
        {"Сумма операции": -100},  # Целое число
        {"Сумма операции": -200.0},  # Float
        {"Сумма операции": -300.75},  # Дробное
    ]

    result = get_card_transactions_info(transactions, "4444")
    assert result["total_spent"] == 600.75
    assert result["cashback"] == 6.01  # 600.75 / 100 = 6.0075 → 6.01


def test_get_card_transactions_info_cashback_calculation():
    """Тест точности расчета кешбека"""
    transactions = [
        {"Сумма операции": -100.01},
        {"Сумма операции": -100.02},
        {"Сумма операции": -100.03},
    ]

    result = get_card_transactions_info(transactions, "5555")
    assert result["total_spent"] == 300.06
    assert result["cashback"] == 3.00  # 300.06 / 100 = 3.0006 → 3.00


def test_get_card_transactions_info_no_negative_transactions():
    """Тест отсутствия трат"""
    transactions = [
        {"Сумма операции": 100.0},
        {"Сумма операции": 0.0},
        {"Сумма операции": math.nan},
    ]

    result = get_card_transactions_info(transactions, "6666")
    assert result["total_spent"] == 0.0
    assert result["cashback"] == 0.0


def test_get_top_transactions_basic_functionality(sample_transactions_top_transactions):
    """Тест базовой функциональности: отбор топ-5 транзакций"""
    result = get_top_transactions(sample_transactions_top_transactions)

    # Ожидаемый порядок: самые большие траты (по модулю)
    expected_amounts = [1500, 1000, 800, 500, 300]

    assert len(result) == 5
    assert [t["amount"] for t in result] == expected_amounts
    assert result[0]["date"] == "05.05.2023"
    assert result[0]["category"] == "Одежда"
    assert result[0]["description"] == "Магазин"


def test_get_top_transactions_less_than_5_transactions():
    """Тест когда транзакций меньше 5"""
    transactions = [
        {"Сумма операции": -300, "Дата платежа": datetime(2023, 1, 1), "Категория": "A", "Описание": "Test1"},
        {"Сумма операции": -100, "Дата платежа": datetime(2023, 1, 2), "Категория": "B", "Описание": "Test2"},
    ]

    result = get_top_transactions(transactions)
    assert len(result) == 2
    assert [t["amount"] for t in result] == [300, 100]


def test_get_top_transactions_positive_transactions():
    """Тест что положительные транзакции учитываются"""
    transactions = [
        {"Сумма операции": -50, "Дата платежа": datetime(2023, 1, 1)},
        {"Сумма операции": 100, "Дата платежа": datetime(2023, 1, 2)},
        {"Сумма операции": -150, "Дата платежа": datetime(2023, 1, 3)},
    ]

    result = get_top_transactions(transactions)
    assert len(result) == 3
    assert [t["amount"] for t in result] == [150, 100, 50]


def test_get_top_transactions_date_formatting():
    """Тест форматирования даты"""
    transactions = [
        {"Сумма операции": -100, "Дата платежа": datetime(2023, 12, 31)},
        {"Сумма операции": -200, "Дата платежа": datetime(2023, 1, 1)},
    ]

    result = get_top_transactions(transactions)
    assert result[0]["date"] == "01.01.2023"
    assert result[1]["date"] == "31.12.2023"


def test_get_top_transactions_sorting_order():
    """Тест правильности порядка сортировки"""
    transactions = [
        {"Сумма операции": -100, "Дата платежа": datetime(2023, 1, 1)},
        {"Сумма операции": -300, "Дата платежа": datetime(2023, 1, 2)},
        {"Сумма операции": -200, "Дата платежа": datetime(2023, 1, 3)},
    ]

    result = get_top_transactions(transactions)
    assert [t["amount"] for t in result] == [300, 200, 100]


def test_get_top_transactions_empty_input():
    """Тест пустого ввода"""
    assert get_top_transactions([]) == []


def test_get_top_transactions_duplicate_amounts():
    """Тест обработки одинаковых сумм"""
    transactions = [
        {"Сумма операции": -500, "Дата платежа": datetime(2023, 5, 1), "Описание": "A"},
        {"Сумма операции": -500, "Дата платежа": datetime(2023, 5, 2), "Описание": "B"},
        {"Сумма операции": -500, "Дата платежа": datetime(2023, 5, 3), "Описание": "C"},
    ]

    result = get_top_transactions(transactions)
    assert len(result) == 3
    # Порядок должен сохраниться как в исходном списке при сортировке
    assert [t["description"] for t in result] == ["A", "B", "C"]


def test_get_top_transactions_mixed_data_types():
    """Тест разных типов данных в суммах"""
    transactions = [
        {"Сумма операции": -100.5, "Дата платежа": datetime(2023, 1, 1)},
        {"Сумма операции": -200, "Дата платежа": datetime(2023, 1, 2)},  # Целое число
    ]

    result = get_top_transactions(transactions)
    # Строка должна интерпретироваться как 0
    assert result[0]["amount"] == 200
    assert result[1]["amount"] == 100.5


def test_get_top_transactions_large_dataset():
    """Тест большого набора данных"""
    transactions = [{"Сумма операции": -i, "Дата платежа": datetime(2023, 1, 1)} for i in range(1, 1001)]
    result = get_top_transactions(transactions)

    assert len(result) == 5
    assert [t["amount"] for t in result] == [1000, 999, 998, 997, 996]


