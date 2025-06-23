from unittest.mock import patch

import pytest


@pytest.fixture
def file_valid_data():
    return [
        {"Дата операции": "01.01.2023 00:00:00", "Дата платежа": "02.01.2023 ", "Сумма": 100},
        {"Дата операции": "02.01.2023 12:30:45", "Дата платежа": "04.01.2023 ", "Сумма": 200}
    ]

