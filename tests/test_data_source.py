import pandas as pd
import pytest
from unittest.mock import patch, mock_open
from components.data_source import CsvDataSource


# Fixtures for reusable components
@pytest.fixture
def data_source():
    return CsvDataSource()

@pytest.fixture
def sample_data():
    data = {
        'column1': ['data1', 'data2'],
        'column2': ['data3', 'data4']
    }
    return pd.DataFrame(data)


# Test Cases
def test_save_data(data_source, sample_data):
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        data_source.save_data(sample_data, 'filename.csv')
        mock_to_csv.assert_called_once_with('filename.csv', index=False)


def test_load_data(data_source):
    # Mocking the pd.read_csv() function to return a dataframe
    mock_df = pd.DataFrame()
    with patch('pandas.read_csv', return_value=mock_df) as mock_read_csv:
        result = data_source.load_data('filename.csv')
        mock_read_csv.assert_called_once_with('filename.csv')
        assert result.equals(mock_df)
