import argparse
import asyncio
import multiprocessing as mp
import os

from components.data_enricher import LeiLookupClient, DataEnricher, LeiLookupCache
from components.data_source import CsvDataSource
from components.data_validator import LEIDataValidator
from components.data_parser import LEIDataParser
from components.transaction_calculator import calculate, TransactionCostsFormula
from globals import Logger

logger = Logger.get_logger(__name__)

from logger.str_tool import boxify


class MainRunner:
    def __init__(self, client=None,
                 cache_size=100,
                 sleep_rate=0.6,
                 retry_attempts=3,
                 log_level='INFO',
                 input_file: str = None,
                 output_file: str = None):

        logger.info('Initializing the components...')
        Logger.set_log_level(log_level)

        self.input_file = input_file
        self.output_file = output_file

        self.data_parser = LEIDataParser()
        self.data_validator = LEIDataValidator()
        self.data_source = CsvDataSource()

        if client == 'LeiLookupClient':
            self.lookup_client = \
                LeiLookupClient(LeiLookupCache(cache_size), sleep_rate=sleep_rate, retry_attempts=retry_attempts)

        else:
            raise NotImplementedError('This client is not implemented yet.')

        self.data_enricher = DataEnricher(client=self.lookup_client, data_parser=self.data_parser)

    async def run(self) -> None:
        logger.info('Starting the enrichment process...')
        df = self.data_source.load_data(self.input_file)

        if not self.data_validator.validate_input_data(df):
            logger.error('Input data validation failed!')
            return

        async with self.lookup_client:
            df = await self.data_enricher.enrich_data(df, df['lei'].tolist())

        df = calculate(df=df, formula=TransactionCostsFormula(), column_name='transaction_costs')

        if not self.data_validator.validate_output_data(df):
            logger.error('Output data validation failed!')
            return

        self.data_source.save_data(df, self.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data enrichment app.')
    parser.add_argument('--client', type=str, default='LeiLookupClient', help='The client.')
    parser.add_argument('--cache_size', type=int, default=100, help='The size of the cache.')
    parser.add_argument('--sleep_rate', type=float, default=0.6, help='The sleep rate between requests.')
    parser.add_argument('--retry_attempts', type=int, default=3, help='The number of retry attempts.')
    parser.add_argument('--log_level', type=str, default='INFO', help='The log level.')
    parser.add_argument('--input_file', type=str, default='data/input_dataset.csv', help='The path to the input file.')
    parser.add_argument('--output_file', type=str, default='data/output_data.csv', help='The path to the output file.')

    args = parser.parse_args()
    arg_dict = vars(args)

    print(boxify('Data Enrichment App', arg_dict))
    asyncio.run(MainRunner(**arg_dict).run())
