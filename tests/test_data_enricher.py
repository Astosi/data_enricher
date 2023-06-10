import pandas as pd
import pytest
from unittest.mock import MagicMock, AsyncMock, call

from components.data_enricher import LeiLookupClient, DataEnricher, IClient
from components.data_parser import LEIDataParser, IDataParser

# Existing data
data = {
    'lei': ['XKZZ2JZF41MRHTR1V493', '213800MBWEIJDM5CU638', 'K6Q0W1PS1L1O4IQL9C32', 'XKZZ2JZF41MRHTR1V493',
            'K6Q0W1PS1L1O4IQL9C32'],
}
df = pd.DataFrame(data)

# Expected enriched data
expected_enriched_data = {
    'lei': ['XKZZ2JZF41MRHTR1V493', '213800MBWEIJDM5CU638', 'K6Q0W1PS1L1O4IQL9C32', 'XKZZ2JZF41MRHTR1V493',
            'K6Q0W1PS1L1O4IQL9C32'],
    'legal_name': ['CITIGROUP GLOBAL MARKETS LIMITED', 'LLOYDS BANK CORPORATE MARKETS PLC',
                   'J.P. MORGAN SECURITIES PLC', 'CITIGROUP GLOBAL MARKETS LIMITED', 'J.P. MORGAN SECURITIES PLC'],
    'bic': ['SBILGB2LXXX', 'LLCMGB22XXX', 'JPMSGB2LXXX', 'SBILGB2LXXX', 'JPMSGB2LXXX'],
    'country': ['GB', 'GB', 'GB', 'GB', 'GB'],
}
expected_df = pd.DataFrame(expected_enriched_data)

# The fetch response for each LEI
lei_responses = {
    'XKZZ2JZF41MRHTR1V493': '[{"data": [{"attributes": {"entity": {"legalName": {"name": "CITIGROUP GLOBAL MARKETS LIMITED"}, "legalAddress": {"country": "GB"}}, "bic": ["SBILGB2LXXX"]}}]}]',
    '213800MBWEIJDM5CU638': '[{"data": [{"attributes": {"entity": {"legalName": {"name": "LLOYDS BANK CORPORATE MARKETS PLC"}, "legalAddress": {"country": "GB"}}, "bic": ["LLCMGB22XXX"]}}]}]',
    'K6Q0W1PS1L1O4IQL9C32': '[{"data": [{"attributes": {"entity": {"legalName": {"name": "J.P. MORGAN SECURITIES PLC"}, "legalAddress": {"country": "GB"}}, "bic": ["JPMSGB2LXXX"]}}]}]',
}


@pytest.mark.asyncio
async def test_enrich_data_integration():
    # Create client and data parser
    client = LeiLookupClient()
    data_parser = LEIDataParser()

    data_enricher = DataEnricher(client=client, data_parser=data_parser)

    # Enrich data

    async with client:
        enriched_df = await data_enricher.enrich_data(df, df['lei'].tolist())

    # Check if the data enrichment was correct
    pd.testing.assert_frame_equal(enriched_df, expected_df)
