import pytest
from components.data_parser import LEIDataParser


# Fixtures for reusable components
@pytest.fixture
def parser():
    return LEIDataParser()

@pytest.fixture
def sample_data():
    return [
        '{"data": [{"attributes": {"entity": {"legalName": {"name": "Company 1"}, "legalAddress": {"country": "GB"}}, "bic": ["1234"]}}]}',
        '{"data": [{"attributes": {"entity": {"legalName": {"name": "Company 2"}, "legalAddress": {"country": "NL"}}, "bic": ["5678"]}}]}'
    ]

@pytest.fixture
def bad_data():
    return ['Bad Data']


# Test Cases
def test_parse_data(parser, sample_data):
    parsed_data = parser.parse_data(sample_data)
    assert parsed_data == [{'legal_name': 'Company 1', 'bic': '1234', 'country': 'GB'},
                           {'legal_name': 'Company 2', 'bic': '5678', 'country': 'NL'}]


def test_parse_data_bad_data(parser, bad_data):
    parsed_data = parser.parse_data(bad_data)
    assert parsed_data == [{'bic': None, 'country': None, 'legal_name': None}]
