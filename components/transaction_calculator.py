from abc import ABC, abstractmethod
from multiprocessing import cpu_count, Pool
from typing import Optional, Callable

import numpy as np
import pandas as pd
from globals import Logger
import multiprocessing as mp

logger = Logger.get_logger(__name__)


class Formula(ABC):
    @abstractmethod
    def apply(self, row: pd.Series) -> Optional[float]:
        pass


class TransactionCostsFormula(Formula):

    def apply(self, row: pd.Series) -> Optional[float]:
        legal_address_country = row['country']
        notional = row['notional']
        rate = row['rate']

        if legal_address_country == 'GB':
            transaction_costs = notional * rate - notional
            logger.info(f"Transaction costs calculated for country 'GB': {transaction_costs}")
            return transaction_costs

        elif legal_address_country == 'NL':
            transaction_costs = abs(notional * (1 / rate) - notional)
            logger.info(f"Transaction costs calculated for country 'NL': {transaction_costs}")
            return transaction_costs
        else:
            logger.warning(f"No transaction costs calculated for unknown country: {legal_address_country}")
            return None


def calculate(df: pd.DataFrame, column_name: str, formula: Formula) -> pd.DataFrame:
    cores = cpu_count()
    pool = Pool(cores)

    # Apply the formula's apply method to each row in the DataFrame
    df[column_name] = pool.map(formula.apply, [row for _, row in df.iterrows()])

    pool.close()
    pool.join()

    return df
