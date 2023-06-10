import pandas as pd
import pytest
from unittest.mock import patch
from components.data_validator import LEIDataValidator


# Fixtures for reusable components
@pytest.fixture
def validator():
    return LEIDataValidator()


@pytest.fixture
def sample_input_data():
    data = {
        'lei': ['lei1', 'lei2'],
        'notional': [1000, 2000],
        'rate': [1.5, 2.0]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_output_data():
    data = {
        'lei': ['lei1', 'lei2'],
        'notional': [1000, 2000],
        'rate': [1.5, 2.0],
        'legal_name': ['Company 1', 'Company 2'],
        'country': ['GB', 'NL'],
        'transaction_costs': [-1500, -4000]
    }
    return pd.DataFrame(data)


# Test Cases
def test_validate_input_data_pass(validator, sample_input_data):
    assert validator.validate_input_data(sample_input_data)


def test_validate_output_data_pass(validator, sample_output_data):
    assert validator.validate_output_data(sample_output_data)


def test_validate_output_data_fail(validator, sample_input_data):
    assert not validator.validate_output_data(sample_input_data)
