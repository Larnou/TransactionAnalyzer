import json
from datetime import datetime
from typing import Any

import pandas as pd
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer


def print_json(data: list[dict[str, Any]]):
    """Печатает данные в виде подсвеченного JSON с обработкой дат"""

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
