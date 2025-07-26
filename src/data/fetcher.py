"""
Data fetching and preprocessing module for Grid Trading Strategy
"""

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataFetcher:
    """Handles data fetching and preprocessing for trading strategies"""
    
    def __init__(self):
        self.data = None
        
    def fetch_data(self, 
                   symbol: str, 
                   start_date: str, 
                   end_date: str, 
                   interval: str = '5m') -> pd.DataFrame:
        """
        Fetch financial data from Yahoo Finance
        
        Args:
            symbol: Trading symbol (e.g., 'EURUSD=X', 'BTC-USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Data interval (1m, 5m, 15m, 1h, 1d, etc.)
            
        Returns:
            pd.DataFrame: OHLCV data
        """
        try:
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
            data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Fix column names if they are MultiIndex
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
                
            self.data = data
            logger.info(f"Successfully fetched {len(data)} data points")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def add_technical_indicators(self, 
                               data: pd.DataFrame, 
                               atr_period: int = 16) -> pd.DataFrame:
        """
        Add technical indicators to the dataset
        
        Args:
            data: OHLCV dataframe
            atr_period: Period for ATR calculation
            
        Returns:
            pd.DataFrame: Data with technical indicators
        """
        df = data.copy()
        
        # Add ATR (Average True Range)
        df['ATR'] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=atr_period)
        
        # Add moving averages for dynamic midprice
        df['MA_20'] = ta.sma(df['Close'], length=20)
        df['MA_50'] = ta.sma(df['Close'], length=50)
        
        # Add Bollinger Bands
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df['BB_Upper'] = bb['BBU_20_2.0']
            df['BB_Lower'] = bb['BBL_20_2.0']
            df['BB_Middle'] = bb['BBM_20_2.0']
        
        # Drop rows with NaN values
        df.dropna(inplace=True)
        
        return df
    
    def get_dynamic_midprice(self, data: pd.DataFrame, method: str = 'ma_20') -> float:
        """
        Calculate dynamic midprice based on different methods
        
        Args:
            data: OHLCV dataframe with indicators
            method: Method to calculate midprice ('ma_20', 'ma_50', 'bb_middle', 'hlc3')
            
        Returns:
            float: Dynamic midprice
        """
        if method == 'ma_20':
            return data['MA_20'].iloc[-1]
        elif method == 'ma_50':
            return data['MA_50'].iloc[-1]
        elif method == 'bb_middle':
            return data['BB_Middle'].iloc[-1] if 'BB_Middle' in data.columns else data['Close'].iloc[-1]
        elif method == 'hlc3':
            return (data['High'].iloc[-1] + data['Low'].iloc[-1] + data['Close'].iloc[-1]) / 3
        else:
            return data['Close'].iloc[-1]
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate the fetched data
        
        Args:
            data: OHLCV dataframe
            
        Returns:
            bool: True if data is valid
        """
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        if data.empty:
            logger.error("Data is empty")
            return False
            
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            return False
            
        if data.isnull().any().any():
            logger.warning("Data contains NaN values")
            
        return True
    
    def get_data_summary(self, data: pd.DataFrame) -> dict:
        """
        Get summary statistics of the data
        
        Args:
            data: OHLCV dataframe
            
        Returns:
            dict: Summary statistics
        """
        return {
            'rows': len(data),
            'start_date': data.index[0].strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': data.index[-1].strftime('%Y-%m-%d %H:%M:%S'),
            'price_range': {
                'min': data['Low'].min(),
                'max': data['High'].max(),
                'current': data['Close'].iloc[-1]
            },
            'volume_stats': {
                'mean': data['Volume'].mean(),
                'total': data['Volume'].sum()
            }
        }
