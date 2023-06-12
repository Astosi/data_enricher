import os
from abc import ABC, abstractmethod
from typing import Callable, Union

from globals import Logger

logger = Logger.get_logger(__name__)

import pandas as pd

def handle_io_errors(is_save_function: bool):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except FileNotFoundError as e:
                logger.error(f"File {e.filename} not found.")
                if is_save_function:
                    return False
                else:
                    return pd.DataFrame()
            except pd.errors.EmptyDataError as e:
                logger.error(f"No data to {('write to file' if is_save_function else 'read from file')}.")
                if is_save_function:
                    return False
                else:
                    return pd.DataFrame()
            except pd.errors.ParserError as e:
                logger.error(f"Error parsing data from file. {e}")
                return pd.DataFrame()
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                if is_save_function:
                    return None
                else:
                    return pd.DataFrame()
        return wrapper
    return decorator


class IDataSource(ABC):

    @abstractmethod
    def save_data(self, file, filename: str):
        pass

    def load_data(self, filename: str):
        pass


class CsvDataSource(IDataSource):
    """
    This class is responsible for saving and loading data from CSV files.
    You can use it as a template for other data sources, e.g. databases.
    """

    @handle_io_errors(is_save_function=True)
    def save_data(self, file: pd.DataFrame, filename: str) -> Union[bool, None]:
        file.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        return True

    @handle_io_errors(is_save_function=False)
    def load_data(self, filename: str) -> pd.DataFrame:
        if not os.path.exists(filename):
            logger.error(f"File {filename} does not exist.")
            return pd.DataFrame()

        data = pd.read_csv(filename)
        logger.info(f"Data loaded from {filename} with shape {data.shape}")
        return data