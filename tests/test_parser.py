import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.parser import read_file_from_csv, read_file_from_xlsx


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
