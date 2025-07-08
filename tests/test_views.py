import json
from unittest.mock import patch

from src.views import main_view, main_event


@patch('src.utils.get_welcome_words')
@patch('src.utils.get_transaction_history')
@patch('src.utils.get_card_numbers')
@patch('src.utils.get_cards_transactions_info')
@patch('src.utils.get_top_transactions')
@patch('src.utils.get_currency_rates')
@patch('src.utils.get_stock_prices')
def test_main_view_basic_structure(
        mock_stock, mock_currency, mock_top, mock_cards,
        mock_card_nums, mock_history, mock_welcome,
        sample_view_transaction_data, sample_user_data
):
    """Проверка базовой структуры выходного JSON"""
    # Мокируем возвращаемые значения
    mock_welcome.return_value = "Добро пожаловать!"
    mock_history.return_value = sample_view_transaction_data
    mock_card_nums.return_value = ['1234****5678', '8765****4321']
    mock_cards.return_value = [
        {"card": "1234****5678", "expenses": 10000, "cashback": 100},
        {"card": "8765****4321", "expenses": 5000, "cashback": 50}
    ]
    mock_top.return_value = [
        {"date": "15.05.2023 16:44:00", "amount": -5000, "category": "Техника"},
        {"date": "10.05.2023 12:44:00", "amount": -4000, "category": "Путешествия"}
    ]
    mock_currency.return_value = [
        {"currency": "USD", "rate": 75.5},
        {"currency": "EUR", "rate": 89.2}
    ]
    mock_stock.return_value = [
        {"stock": "AAPL", "price": 150.25},
        {"stock": "GOOGL", "price": 2800.75}
    ]

    period_end = "31.05.2023 16:44:00"
    result = main_view(sample_view_transaction_data, sample_user_data, period_end)
    result_dict = json.loads(result)

    # Проверяем структуру
    assert "greeting" in result_dict
    assert "cards" in result_dict
    assert "top_transactions" in result_dict
    assert "currency_rates" in result_dict
    assert "stock_prices" in result_dict

    # Проверяем типы данных
    assert isinstance(result_dict["greeting"], str)
    assert isinstance(result_dict["cards"], list)
    assert isinstance(result_dict["top_transactions"], list)
    assert isinstance(result_dict["currency_rates"], list)
    assert isinstance(result_dict["stock_prices"], list)


@patch('src.utils.get_transaction_history_ranged')
@patch('src.utils.get_total_expenses_amount')
@patch('src.utils.get_categories')
@patch('src.utils.get_expenses_by_top_categories')
@patch('src.utils.get_transfers_and_cash')
@patch('src.utils.get_total_income_amount')
@patch('src.utils.get_income_categories')
@patch('src.utils.get_currency_rates')
@patch('src.utils.get_stock_prices')
def test_main_event_basic_structure(
        mock_stock, mock_currency, mock_income_cats, mock_total_income,
        mock_transfers, mock_expenses_top, mock_cats, mock_total_expenses,
        mock_history,
        sample_view_transaction_data, sample_user_data
):
    """Проверка базовой структуры выходного JSON"""
    # Мокируем возвращаемые значения
    mock_history.return_value = sample_view_transaction_data.to_dict('records')
    mock_total_expenses.return_value = 15000
    mock_cats.return_value = ['Еда', 'Транспорт', 'Развлечения']
    mock_expenses_top.return_value = [
        {"category": "Еда", "amount": 5000},
        {"category": "Транспорт", "amount": 4000}
    ]
    mock_transfers.return_value = [
        {"category": "Переводы", "amount": 3000},
        {"category": "Наличные", "amount": 2000}
    ]
    mock_total_income.return_value = 50000
    mock_income_cats.return_value = [
        {"category": "Зарплата", "amount": 40000},
        {"category": "Бонусы", "amount": 10000}
    ]
    mock_currency.return_value = [
        {"currency": "USD", "rate": 75.5},
        {"currency": "EUR", "rate": 89.2}
    ]
    mock_stock.return_value = [
        {"stock": "AAPL", "price": 150.25},
        {"stock": "GOOGL", "price": 2800.75}
    ]

    period_end = "31.05.2023 16:44:00"
    result = main_event(sample_view_transaction_data, sample_user_data, period_end, "M")
    result_dict = json.loads(result)

    # Проверяем структуру
    assert "expenses" in result_dict
    assert "income" in result_dict
    assert "currency_rates" in result_dict
    assert "stock_prices" in result_dict

    # Проверяем вложенную структуру expenses
    expenses = result_dict["expenses"]
    assert "total_amount" in expenses
    assert "main" in expenses
    assert "transfers_and_cash" in expenses

    # Проверяем вложенную структуру income
    income = result_dict["income"]
    assert "total_amount" in income
    assert "main" in income
