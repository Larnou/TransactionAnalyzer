import os
from datetime import timedelta, datetime

import numpy as np
import pandas as pd

from src.utils import print_json

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

def read_file_from_csv(filename: str, home_directiry: str = None) -> list[dict]:
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

    xlsx_operations = csv_data.to_dict("records")
    return xlsx_operations


def read_file_from_xlsx(filename: str, home_directiry: str = None) -> list[dict]:
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

    xlsx_operations = xlsx_data.to_dict("records")
    return xlsx_operations
