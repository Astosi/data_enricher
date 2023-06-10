import pandas as pd
import pytest
from unittest.mock import Mock, patch

from components.transaction_calculator import Formula, calculate, TransactionCostsFormula


class DummyFormula(Formula):
    def apply(self, row):
        return row['x'] * 2

@pytest.fixture
def mock_logger():
    return Mock()

@patch('components.transaction_calculator.cpu_count')
def test_calculate(mock_cpu_count, mock_logger):
    # Mock cpu_count to return a known value
    mock_cpu_count.return_value = 4

    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': ['a', 'b', 'c']
    })

    df = calculate(df, 'z', DummyFormula())

    assert 'z' in df.columns
    assert df['z'].tolist() == [2, 4, 6]

@patch('components.transaction_calculator.logger')
def test_transaction_costs_formula(mock_logger):
    formula = TransactionCostsFormula()

    row_gb = pd.Series({
        'country': 'GB',
        'notional': 100,
        'rate': 0.2
    })

    assert formula.apply(row_gb) == -80  # 100 * 0.2 - 100

    row_nl = pd.Series({
        'country': 'NL',
        'notional': 100,
        'rate': 0.2
    })

    assert formula.apply(row_nl) == 400  # abs(100 * (1 / 0.2) - 100)

    row_other = pd.Series({
        'country': 'US',
        'notional': 100,
        'rate': 0.2
    })

    assert formula.apply(row_other) is None
    mock_logger.warning.assert_called_with("No transaction costs calculated for unknown country: US")
