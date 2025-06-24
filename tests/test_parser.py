import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.parser import read_file_from_csv, read_file_from_xlsx, print_json


def create_test_csv(filename: Path, data: list[dict]):
    """Создает CSV файл из списка словарей"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')

def test_csv_valid(tmp_path, file_valid_data):
    test_csv = tmp_path / "test.csv"
    create_test_csv(test_csv, file_valid_data)

    result = read_file_from_csv("test.csv", home_directiry=str(tmp_path))

    assert len(result) == len(file_valid_data)
    assert result[0]['Сумма'] == 100

def test_csv_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_file_from_csv("non_existent.csv", home_directiry=str(tmp_path))

def test_csv_different_date_formats(tmp_path, file_different_dates_formats):
    test_csv = tmp_path / "dates.csv"
    create_test_csv(test_csv, file_different_dates_formats)

    result = read_file_from_csv("dates.csv", home_directiry=str(tmp_path))

    # Проверяем что все даты либо преобразованы, либо None
    for i, item in enumerate(result):
        if i == 0:
            assert isinstance(item['Дата операции'], datetime)
            assert item['Дата операции'].day == 1
        elif i == 4:
            assert item['Дата операции'] is None
        else:
            assert isinstance(item['Дата операции'], datetime) or item['Дата операции'] is None

# Тестирование функции чтения ELSX файлов
def create_test_xlsx(filename: Path, data: list[dict]):
    """Создает CSV файл из списка словарей"""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

def test_xlsx_valid(tmp_path, file_valid_data):
    test_xlsx = tmp_path / "test.xlsx"
    create_test_xlsx(test_xlsx, file_valid_data)

    result = read_file_from_xlsx("test.xlsx", home_directiry=str(tmp_path))

    assert len(result) == len(file_valid_data)
    assert result[0]['Сумма'] == 100


def test_xlsx_date_edge_cases(tmp_path, file_different_dates):
    test_xlsx = tmp_path / "edge_dates.xlsx"
    create_test_xlsx(test_xlsx, file_different_dates)

    result = read_file_from_xlsx("edge_dates.xlsx", home_directiry=str(tmp_path))

    # Проверяем корректные даты
    assert result[0]['Дата операции'].strftime("%d.%m.%Y %H:%M:%S") == "31.12.2023 23:59:59"
    assert result[1]['Дата операции'].strftime("%d.%m.%Y %H:%M:%S") == "01.01.2023 00:00:00"
    assert result[2]['Дата операции'].year == 2024
    assert result[2]['Дата операции'].month == 2
    assert result[2]['Дата операции'].day == 29

    # Проверяем невалидную дату
    assert result[4]['Дата операции'] is None

def test_xlsx_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_file_from_xlsx("non_existent.xlsx", home_directiry=str(tmp_path))


def test_xlsx_different_date_formats(tmp_path, file_different_dates_formats):
    test_xlsx = tmp_path / "dates.xlsx"
    create_test_xlsx(test_xlsx, file_different_dates_formats)

    result = read_file_from_xlsx("dates.xlsx", home_directiry=str(tmp_path))

    # Проверяем что все даты либо преобразованы, либо None
    for i, item in enumerate(result):
        if i == 0:
            assert isinstance(item['Дата операции'], datetime)
            assert item['Дата операции'].day == 1
        elif i == 4:
            assert item['Дата операции'] is None
        else:
            assert isinstance(item['Дата операции'], datetime) or item['Дата операции'] is None


def test_xlsx_multiple_sheets(tmp_path, file_valid_data, file_valid_one_line_data):
    test_xlsx = tmp_path / "multi_sheet.xlsx"

    # Создаем файл с несколькими листами
    with pd.ExcelWriter(test_xlsx, engine='openpyxl') as writer:
        pd.DataFrame(file_valid_one_line_data).to_excel(writer, sheet_name="Sheet1", index=False)
        pd.DataFrame(file_valid_data).to_excel(writer, sheet_name="Sheet2", index=False)

    # Функция должна читать первый лист по умолчанию
    result = read_file_from_xlsx("multi_sheet.xlsx", home_directiry=str(tmp_path))

    assert len(result) == 1


def test_datetime_conversion(sample_data):
    """Тестирование преобразования объектов datetime в строки"""
    # Создаем мок для внешних зависимостей
    with patch('json.dumps') as mock_dumps, \
            patch('pygments.highlight') as mock_highlight, \
            patch('builtins.print') as mock_print:
        # Вызываем тестируемую функцию
        print_json(sample_data)

        # Получаем аргумент, переданный в json.dumps
        converted_data = mock_dumps.call_args[0][0]

        # Проверяем преобразование дат
        assert converted_data[0]['date'] == "2023.01.01 12:00:00"
        assert converted_data[1]['date'] == "2023.01.02 15:30:00"
        assert converted_data[0]['value'] == 100


def test_nested_datetime_conversion(nested_data):
    """Тестирование преобразования вложенных структур"""
    with patch('json.dumps') as mock_dumps, \
            patch('pygments.highlight'), \
            patch('builtins.print'):
        print_json([nested_data])
        converted_data = mock_dumps.call_args[0][0][0]

        assert converted_data['dates'][0] == "2023.01.03 08:00:00"
        assert converted_data['info']['created_at'] == "2023.01.04 10:00:00"
        assert converted_data['info']['items'][0]['time'] == "2023.01.05 12:00:00"


def test_json_dumps_called_correctly(sample_data):
    """Тестирование параметров вызова json.dumps"""
    with patch('json.dumps') as mock_dumps, \
            patch('pygments.highlight'), \
            patch('builtins.print'):
        print_json(sample_data)

        # Проверяем параметры вызова
        args, kwargs = mock_dumps.call_args
        assert kwargs['indent'] == 4
        assert kwargs['ensure_ascii'] is False
        assert kwargs['default'] == str


def test_non_serializable_objects():
    """Тестирование обработки неподдерживаемых типов"""

    class CustomType:
        pass

    test_data = [{"custom": CustomType()}]

    with patch('json.dumps') as mock_dumps, \
            patch('pygments.highlight'), \
            patch('builtins.print'):
        print_json(test_data)

        # Проверяем, что используется default=str
        kwargs = mock_dumps.call_args[1]
        assert kwargs['default'] == str