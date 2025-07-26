"""
Configuration settings for the Grid Trading Strategy
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class TradingConfig:
    """Configuration for trading parameters"""
    grid_distance: float = 5.0      # Default for stocks
    grid_range: float = 50.0        # Default range
    cash: float = 10000             # Starting capital
    margin: float = 0.01            # 1% margin
    max_trades: int = 5             # Max concurrent trades
    atr_multiplier: float = 1.5     # Stop loss multiplier
    tp_sl_ratio: float = 0.6        # Take profit ratio
    position_size: float = 100      # Position size (shares/units)
    atr_period: int = 14            # ATR calculation period


@dataclass
class DataConfig:
    """Configuration for data fetching"""
    interval: str = '1d'  # Use daily data for reliable access
    start_date: str = '2024-01-01'
    end_date: str = '2024-12-31'


# Supported assets with their default midprices, grid parameters, and recommended range
# Prices updated as of July 2025
SUPPORTED_ASSETS = {
    # Stocks - Major Tech
    'AAPL': {'midprice': 214, 'grid_distance': 3, 'grid_range': 30, 'name': 'Apple'},
    'TSLA': {'midprice': 316, 'grid_distance': 8, 'grid_range': 80, 'name': 'Tesla'},
    'MSFT': {'midprice': 514, 'grid_distance': 8, 'grid_range': 80, 'name': 'Microsoft'},
    'GOOGL': {'midprice': 193, 'grid_distance': 3, 'grid_range': 30, 'name': 'Google'},
    'NVDA': {'midprice': 174, 'grid_distance': 5, 'grid_range': 50, 'name': 'NVIDIA'},
    'AMD': {'midprice': 166, 'grid_distance': 4, 'grid_range': 40, 'name': 'AMD'},
    'META': {'midprice': 713, 'grid_distance': 8, 'grid_range': 80, 'name': 'Meta'},
    'AMZN': {'midprice': 231, 'grid_distance': 4, 'grid_range': 40, 'name': 'Amazon'},
    'NFLX': {'midprice': 1180, 'grid_distance': 15, 'grid_range': 150, 'name': 'Netflix'},
    'CRM': {'midprice': 269, 'grid_distance': 5, 'grid_range': 50, 'name': 'Salesforce'},
    'ADBE': {'midprice': 371, 'grid_distance': 6, 'grid_range': 60, 'name': 'Adobe'},
    'PYPL': {'midprice': 78, 'grid_distance': 2, 'grid_range': 20, 'name': 'PayPal'},
    'UBER': {'midprice': 91, 'grid_distance': 2, 'grid_range': 20, 'name': 'Uber'},
    'SNOW': {'midprice': 220, 'grid_distance': 4, 'grid_range': 40, 'name': 'Snowflake'},
    'PLTR': {'midprice': 159, 'grid_distance': 4, 'grid_range': 40, 'name': 'Palantir'},
    
    # Banking & Finance
    'JPM': {'midprice': 299, 'grid_distance': 4, 'grid_range': 40, 'name': 'JPMorgan Chase'},
    'BAC': {'midprice': 48, 'grid_distance': 1, 'grid_range': 10, 'name': 'Bank of America'},
    'GS': {'midprice': 729, 'grid_distance': 8, 'grid_range': 80, 'name': 'Goldman Sachs'},
    'MS': {'midprice': 143, 'grid_distance': 3, 'grid_range': 30, 'name': 'Morgan Stanley'},
    'V': {'midprice': 357, 'grid_distance': 5, 'grid_range': 50, 'name': 'Visa'},
    'MA': {'midprice': 568, 'grid_distance': 8, 'grid_range': 80, 'name': 'Mastercard'},
    
    # ETFs - Major Indices
    'SPY': {'midprice': 637, 'grid_distance': 5, 'grid_range': 50, 'name': 'S&P 500 ETF'},
    'QQQ': {'midprice': 566, 'grid_distance': 6, 'grid_range': 60, 'name': 'NASDAQ ETF'},
    'DIA': {'midprice': 449, 'grid_distance': 4, 'grid_range': 40, 'name': 'Dow Jones ETF'},
    'IWM': {'midprice': 224, 'grid_distance': 3, 'grid_range': 30, 'name': 'Russell 2000 ETF'},
    
    # ETFs - Sectors
    'XLF': {'midprice': 53, 'grid_distance': 1, 'grid_range': 10, 'name': 'Financial Sector ETF'},
    'XLK': {'midprice': 262, 'grid_distance': 3, 'grid_range': 30, 'name': 'Technology Sector ETF'},
    'XLE': {'midprice': 87, 'grid_distance': 2, 'grid_range': 20, 'name': 'Energy Sector ETF'},
    
    # Cryptocurrencies - Major
    'BTC-USD': {'midprice': 117600, 'grid_distance': 2000, 'grid_range': 20000, 'name': 'Bitcoin'},
    'ETH-USD': {'midprice': 3738, 'grid_distance': 80, 'grid_range': 800, 'name': 'Ethereum'},
    'SOL-USD': {'midprice': 186, 'grid_distance': 5, 'grid_range': 50, 'name': 'Solana'},
    'ADA-USD': {'midprice': 0.83, 'grid_distance': 0.02, 'grid_range': 0.2, 'name': 'Cardano'},
    'DOT-USD': {'midprice': 4.12, 'grid_distance': 0.15, 'grid_range': 1.5, 'name': 'Polkadot'},
    'AVAX-USD': {'midprice': 24, 'grid_distance': 0.8, 'grid_range': 8, 'name': 'Avalanche'},
    
    # Forex - Major Pairs
    'EURUSD=X': {'midprice': 1.174, 'grid_distance': 0.005, 'grid_range': 0.05, 'name': 'EUR/USD'},
    'GBPUSD=X': {'midprice': 1.344, 'grid_distance': 0.006, 'grid_range': 0.06, 'name': 'GBP/USD'},
    'USDJPY=X': {'midprice': 147.6, 'grid_distance': 0.5, 'grid_range': 5, 'name': 'USD/JPY'},
    'USDCHF=X': {'midprice': 0.794, 'grid_distance': 0.003, 'grid_range': 0.03, 'name': 'USD/CHF'},
    'AUDUSD=X': {'midprice': 0.657, 'grid_distance': 0.003, 'grid_range': 0.03, 'name': 'AUD/USD'},
    'USDCAD=X': {'midprice': 1.37, 'grid_distance': 0.005, 'grid_range': 0.05, 'name': 'USD/CAD'},
    'EURGBP=X': {'midprice': 0.874, 'grid_distance': 0.003, 'grid_range': 0.03, 'name': 'EUR/GBP'},
    
    # Commodities & Energy
    'GC=F': {'midprice': 3339, 'grid_distance': 50, 'grid_range': 500, 'name': 'Gold Futures'},
    'SI=F': {'midprice': 38.3, 'grid_distance': 1.0, 'grid_range': 10, 'name': 'Silver Futures'},
    'CL=F': {'midprice': 65.1, 'grid_distance': 2.0, 'grid_range': 20, 'name': 'Crude Oil'},
    'SLV': {'midprice': 34.7, 'grid_distance': 0.8, 'grid_range': 8, 'name': 'Silver ETF'},
    'USO': {'midprice': 74.9, 'grid_distance': 2, 'grid_range': 20, 'name': 'Oil ETF'},
    'UNG': {'midprice': 13.8, 'grid_distance': 0.4, 'grid_range': 4, 'name': 'Natural Gas ETF'},
    'DBA': {'midprice': 26.1, 'grid_distance': 0.5, 'grid_range': 5, 'name': 'Agriculture ETF'},
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': 'Grid Trading Strategy Backtester',
    'page_icon': '📈',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}
