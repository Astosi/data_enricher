import logging
import json
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from globals import Logger

logger = Logger.get_logger(__name__)
class IDataParser(ABC):

    @staticmethod
    @abstractmethod
    def parse_data(data):
        pass


class LEIDataParser(IDataParser):
    @staticmethod
    def parse_legal_name(item: dict) -> str:
        try:
            return item['data'][0]['attributes']['entity']['legalName']['name']
        except (KeyError, IndexError) as e:
            logger.warning(f'Failed to parse legal name from data. \n {e}')
            return ''

    @staticmethod
    def parse_bic(item: dict) -> str:
        try:
            return item['data'][0]['attributes']['bic'][0]
        except (KeyError, IndexError) as e:
            logger.warning(f'Failed to parse BIC from data. \n {e}')
            return ''

    @staticmethod
    def parse_country(item: dict) -> str:
        try:
            return item['data'][0]['attributes']['entity']['legalAddress']['country']
        except (KeyError, IndexError) as e:
            logger.warning(f'Failed to parse country from data. \n {e}')
            return ''

    @classmethod
    def parse_data(cls, data: List[str]) -> List[Dict]:
        """
        Parses the data into a list of dictionaries. If there is any changes in json structure,
        this function does not need to be changed. Just change the parse functions above.

        :param data: The list of API response strings.
        :return: The parsed data as a list of dictionaries.
        """
        parsed_data = []
        for item in data:
            try:
                item = json.loads(item)
                legal_name = cls.parse_legal_name(item)
                bic = cls.parse_bic(item)
                country = cls.parse_country(item)
                parsed_data.append({
                    'legal_name': legal_name,
                    'bic': bic,
                    'country': country,
                })
            except (IndexError, KeyError, json.JSONDecodeError, TypeError) as e:
                parsed_data.append({'legal_name': None, 'bic': None, 'country': None})
                logger.error(f'Error occurred while parsing data. \n {e}' )
        return parsed_data
