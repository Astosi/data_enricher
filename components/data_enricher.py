import aiohttp
import asyncio
from typing import Optional, List
from collections import OrderedDict

import pandas as pd
from aiohttp import ClientError

from components.cacher import ICache, LeiLookupCache
from components.data_parser import IDataParser
from globals import Logger

logger = Logger.get_logger(__name__)
from abc import ABC, abstractmethod
from aiohttp import ClientError


class IClient(ABC):
    @abstractmethod
    async def fetch(self, id_: str) -> Optional[str]:
        pass


class LeiLookupClient(IClient):
    """
    Client for fetching data from the Lei Lookup API.

    This class provides the functionality to interact with the gleif API using LEI(Legal Entity Identifier) and
     retrieve data from it.
    It implements the `IClient` interface, which defines the contract for client implementations.

    The client uses a cache to store the data fetched from the server to avoid . The cache implementation is
    defined by the `ICache` interface, which defines the contract for cache implementations.

    The client uses aiohttp library for asynchronous requests. The session is initialized when the client is
    initialized and closed when the client is closed.

    The client uses a simple rate limiting approach to avoid overwhelming the server with requests.
    The default rate limit is 0.6 seconds between requests, which means that the client will wait for 0.6 seconds

    """
    def __init__(self, cache: ICache = LeiLookupCache(100), sleep_rate: float = 0.6, retry_attempts: int = 3):
        """
        :param cache: An instance of the cache to store fetched data. Default is LeiLookupCache with a cache size of 100.
        :param sleep_rate: The rate at which to pause between requests to adhere to rate limiting. Default is 0.6 seconds.
        :param retry_attempts: The number of retry attempts in case of failed requests. Default is 3 attempts.
        """
        self.session = None
        self.cache = cache
        self.base_url = 'https://api.gleif.org/api/v1/lei-records?filter[lei]='
        self.rate_limit_pause = sleep_rate
        self.retry_attempts = retry_attempts

    async def fetch(self, id_: str) -> Optional[str]:
        data = self.cache.get(id_)
        if data:
            logger.info(f'Fetching data for ID {id_} from cache.')
            return data

        try:
            url = f'{self.base_url}{id_}'
            for attempt in range(self.retry_attempts):
                async with self.session.get(url, ssl=False) as response:
                    # Check if the response is successful
                    if response.status == 200:
                        data = await response.text()

                        # Add the data to the cache to avoid fetching it again
                        self.cache.add(id_, data)

                        await asyncio.sleep(self.rate_limit_pause)
                        logger.info(f'Fetched data for ID {id_} from the server.')
                        return data
                    else:
                        logger.warning(
                            f'Response code {response.status} received for ID {id_}. '
                            f'Retrying ({attempt + 1}/{self.retry_attempts})...')
                        await asyncio.sleep(1)  # Wait for 1 second before retrying

            logger.error(f'Reached maximum retry attempts for ID {id_}. Unable to fetch data.')
            return None

        except ClientError as e:
            logger.error(f'An error occurred during fetch for ID {id_}: {e}')
            return None

    async def close(self) -> None:
        if not self.session.closed:
            await self.session.close()

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    # If you want to use it with the `with` statement, auto-initialize and close the session
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class DataEnricher:
    def __init__(self, client: IClient, data_parser: IDataParser):
        """
               Initializes the DataEnricher.

               :param client: An instance of the client used to fetch data from the API. It's injected as a dependency.
               :param data_parser: An instance of the parser used to parse the fetched data. Check the `IDataParser`
        """
        self.client = client
        self.data_parser = data_parser

    async def enrich_data(self, df, ids: List[str]):
        tasks = [self.client.fetch(id_) for id_ in ids]
        responses = await asyncio.gather(*tasks)

        # Parse the responses into a list of dicts
        parsed_responses = self.data_parser.parse_data(responses)

        # Convert the parsed responses to a DataFrame
        response_df = pd.DataFrame(parsed_responses)

        # Reset index of the original DataFrame
        df.reset_index(drop=True, inplace=True)

        # Concatenate the response data with the original DataFrame
        enriched_df = pd.concat([df, response_df], axis=1)

        return enriched_df
