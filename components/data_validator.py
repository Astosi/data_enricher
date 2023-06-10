from abc import ABC, abstractmethod
import pandas as pd
from pandas.api.types import is_numeric_dtype
from globals import Logger

logger = Logger.get_logger(__name__)



class IDataValidator(ABC):
    @abstractmethod
    def validate_input_data(self, df: pd.DataFrame) -> bool:
        pass

    @abstractmethod
    def validate_output_data(self, df: pd.DataFrame) -> bool:
        pass


class LEIDataValidator(IDataValidator):
    def validate_input_data(self, df: pd.DataFrame) -> bool:
        expected_columns = ['lei', 'notional', 'rate']
        missing_columns = [col for col in expected_columns if col not in df.columns]

        if missing_columns:
            logger.warning("Input data does not match the expected structure!")
            logger.warning("Missing columns: %s", ', '.join(missing_columns))
            return False

        if not is_numeric_dtype(df['notional']) or not is_numeric_dtype(df['rate']):
            logger.warning("Columns 'notional' and 'rate' should be numeric!")
            return False

        logger.info("Input data validated successfully!")
        return True

    def validate_output_data(self, df: pd.DataFrame) -> bool:
        expected_columns = ['lei', 'notional', 'rate', 'legal_name', 'country', 'transaction_costs']
        missing_columns = [col for col in expected_columns if col not in df.columns]

        if missing_columns:
            logger.warning("Output data does not match the expected structure!")
            logger.warning("Missing columns: %s", ', '.join(missing_columns))
            return False

        if df['legal_name'].isnull().any() or df['country'].isnull().any():
            logger.warning("Some rows have not been correctly enriched!")
            return False

        logger.info("Output data validated successfully!")
        return True
