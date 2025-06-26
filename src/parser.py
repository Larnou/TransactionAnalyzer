import json
import os
from datetime import timedelta, datetime
from typing import Any

import numpy as np
import pandas as pd
from pandas import DataFrame
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer


# Список примеров и форматов дат
# formats = [
#     '%d.%m.%Y %H:%M:%S',  # 15.05.2023 14:30:00
#     '%d.%m.%Y',  # 15.05.2023
#     '%Y-%m-%d %H:%M:%S',  # 2023-05-15 14:30:00
#     '%Y/%m/%d %H:%M:%S',  # 2023/05/15 14:30:00
#     '%d-%b-%Y %H:%M:%S',  # 15-May-2023 14:30:00
#     '%d %B %Y %H:%M:%S',  # 15 мая 2023 14:30:00
#     '%Y%m%d%H%M%S',  # 20230515143000
# ]

def read_file_from_csv(filename: str, home_directiry: str = None) -> DataFrame:
    """
    Чтение csv-файла и его псоледущее преобразование в список словарей с ключами колонками исходного файла.
    Args:
        filename: Путь до загружаемого файла
        home_directiry: Директория хранения файлов

    Returns: Список словарей с ключами названиями колонок csv-файла.
    """

    if home_directiry is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_PATH = os.path.join(BASE_DIR, "data", filename)
    else:
        DATA_PATH = os.path.join(home_directiry, filename)

    csv_data = pd.read_csv(DATA_PATH, sep=",", encoding="utf-8")
    csv_data = csv_data.dropna(how="all")

    # Альтернативный вариант с pandas (если все даты в одном формате)
    csv_data['Дата операции'] = pd.to_datetime(
        csv_data['Дата операции'],
        format='%d.%m.%Y %H:%M:%S',
        errors='coerce',
        dayfirst=True
    )

    csv_data['Дата платежа'] = pd.to_datetime(
        csv_data['Дата платежа'],
        format='%d.%m.%Y',
        errors='coerce',
        dayfirst=True
    )

    # Замена оставшихся проблемных значений
    csv_data['Дата операции'] = csv_data['Дата операции'].replace({np.nan: None})
    csv_data['Дата платежа']  = csv_data['Дата платежа'].replace({np.nan: None})

    # xlsx_operations = csv_data.to_dict("records")
    return csv_data


def read_file_from_xlsx(filename: str, home_directiry: str = None) -> DataFrame:
    """
    Чтение xlsx-файла и его псоледущее преобразование в список словарей с ключами колонками исходного файла.
    Args:
        filename: Путь до загружаемого файла
        home_directiry: Директория хранения файлов

    Returns: Список словарей с ключами названиями колонок xlsx-файла.
    """
    if home_directiry is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_PATH = os.path.join(BASE_DIR, "data", filename)
    else:
        DATA_PATH = os.path.join(home_directiry, filename)

    # Читаем как строку для последующей обработки
    xlsx_data = pd.read_excel(DATA_PATH, engine='openpyxl', dtype={'Дата операции': str}, sheet_name=0)
    xlsx_data = xlsx_data.dropna(how="all")

    # Альтернативный вариант с pandas (если все даты в одном формате)
    xlsx_data['Дата операции'] = pd.to_datetime(
        xlsx_data['Дата операции'],
        format='%d.%m.%Y %H:%M:%S',
        errors='coerce',
        dayfirst=True
    )

    xlsx_data['Дата платежа'] = pd.to_datetime(
        xlsx_data['Дата платежа'],
        format='%d.%m.%Y',
        errors='coerce',
        dayfirst=True
    )

    # Замена оставшихся проблемных значений
    xlsx_data['Дата операции'] = xlsx_data['Дата операции'].replace({np.nan: None})
    xlsx_data['Дата платежа']  = xlsx_data['Дата платежа'].replace({np.nan: None})

    # xlsx_operations = xlsx_data.to_dict("records")
    return xlsx_data


def print_json(data: list[dict[str, Any]] | dict[str, Any] | str):
    """
    Печатает данные в виде подсвеченного JSON с обработкой дат
    Args:
        data: Данные в формате list или dict для отображения
    """

    # Рекурсивная функция для преобразования дат
    def convert_datetime(obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.strftime("%Y.%m.%d %H:%M:%S")
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        else:
            return obj

    if type(data) is str:
        json_str = json.loads(data)

        # Сериализуем и печатаем
        json_dict = json.dumps(
            json_str,
            indent=4,
            ensure_ascii=False,
            default=str  # Дополнительная страховка
        )
        print(highlight(json_dict, JsonLexer(), TerminalFormatter()))

    else:
        # Преобразуем все даты в данных
        converted_data = convert_datetime(data)

        # Сериализуем и печатаем
        json_str = json.dumps(
            converted_data,
            indent=4,
            ensure_ascii=False,
            default=str  # Дополнительная страховка
        )
        print(highlight(json_str, JsonLexer(), TerminalFormatter()))


def read_file_from_json(filename: str, home_directiry: str = None) -> list[Any] | Any:
    """
    Чтение xlsx-файла и его псоледущее преобразование в список словарей с ключами колонками исходного файла.
    Args:
        filename: Путь до загружаемого файла
        home_directiry: Директория хранения файлов

    Returns: Список словарей с ключами названиями колонок xlsx-файла.
    """
    """
    Чтение файла формата JSON.
    :param filename: Путь до файла.
    :return: Данные файла JSON или пустой список, если произошла ошибка чтения.
    """
    if home_directiry is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_PATH = os.path.join(BASE_DIR, "data", filename)
    else:
        DATA_PATH = os.path.join(home_directiry, filename)

    try:
        with open(DATA_PATH, encoding="utf8") as f:
            data = json.load(f)

        return data
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError, PermissionError, IsADirectoryError):
        return []
