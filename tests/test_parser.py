import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.parser import read_file_from_csv


def create_test_csv(filename: Path, data: list[dict]):
    """Создает CSV файл из списка словарей"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')

def create_test_xlsx(filename: Path, data: list[dict]):
    """Создает CSV файл из списка словарей"""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, encoding='utf-8')

def test_csv_valid(tmp_path, file_valid_data):
    test_csv = tmp_path / "test.csv"
    create_test_csv(test_csv, file_valid_data)

    result = read_file_from_csv("test.csv", home_directiry=str(tmp_path))

    assert len(result) == len(file_valid_data)
    assert result[0]['Сумма'] == 100


def test_xlsx_valid(tmp_path, file_valid_data):
    test_xlsx = tmp_path / "test.xlsx"
    create_test_csv(test_xlsx, file_valid_data)

    result = read_file_from_csv("test.xlsx", home_directiry=str(tmp_path))

    assert len(result) == len(file_valid_data)
    assert result[0]['Сумма'] == 100
