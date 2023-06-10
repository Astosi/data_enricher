from abc import ABC, abstractmethod
from globals import Logger

logger = Logger.get_logger(__name__)

import pandas as pd

class IDataSource(ABC):

    @abstractmethod
    def save_data(self, file, filename: str):
        pass

    def load_data(self, filename: str):
        pass


class CsvDataSource(IDataSource):

    def save_data(self, file: pd.DataFrame, filename: str):
        try:
            file.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error occurred while saving data: {e}")

    def load_data(self, filename: str) -> pd.DataFrame:
        try:
            data = pd.read_csv(filename)
            logger.info(f"Data loaded from {filename} with shape {data.shape}")
            return data
        except Exception as e:
            logger.error(f"Error occurred while loading data: {e}")
            return pd.DataFrame()
