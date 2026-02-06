from __future__ import annotations 
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd 

@dataclass(frozen=True)
class PriceDataConfig:
    """
    Explain what this part does
    """
    tickers: list[str]
    start: str #Year - Month - Date format 
    end: Optional[str] = None # None means that the date is set to today
    price_field: str = "Close"

def fetch_prices_yfinance (cfg: PriceDataConfig) -> pd.DataFrame:
        """
        Explain what this part does
        """
        try:
            import yfinance as yf
        except ImportError as e:
            raise ImportError(f"Missing dependency from yfinance. Download the latest with: pip install yfinance.")
    
        data = yf.download(
        tickers = cfg.tickers,
        start = cfg.start,
        end = cfg.end,
        auto_adjust = False,
        progress = False,
        group_by = "column",
        
        )

        # During multiple tickers yfinance can return MultiIndex columns
        
        if isinstance(data.columns, pd.MultiIndex):
            if cfg.price_field not in data.columns.levels[0]:
                raise ValueError(f"Price field '{cfg.price_field}' not found. Available: {list(data.columns.levels[0])}")
            prices = data[cfg.price_field].copy()
        else:
            # single ticker
            if cfg.price_field not in data.columns:
                raise ValueError(f"Price field '{cfg.price_field}' not found. Available: {list(data.columns)}")
        prices = data[[cfg.price_field]].copy()
        prices.columns = cfg.tickers

        prices = prices.dropna(how="all")
        return prices
    
def prices_to_returns (prices: pd.DataFrame, method: str = "simple") -> pd.DataFrame:
     """
     Explain what this part does 
     """
     prices = prices.sort_index ()

     if method == "simple":
          rets = prices.pct_change()
     elif method == "log":
        rets = (prices / prices.shift(1)).applymap(lambda x: None if pd.isna(x) else x)
        rets = (prices / prices.shift(1)).apply(lambda s: (s).apply(lambda x: None if pd.isna(x) else x))
        rets = (prices / prices.shift(1))
        import numpy as np
        rets = np.log(rets)

     else:
        raise ValueError("method must be 'simple' or 'log'")
     
     return rets.dropna(how="any")

