import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer

from src.utils import print_json


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

