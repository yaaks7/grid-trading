"""
Grid Trading Strategy Implementation
"""

import numpy as np
import pandas as pd
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class GridGenerator:
    """Generates and manages trading grids"""
    
    def __init__(self, midprice: float, grid_distance: float, grid_range: float):
        """
        Initialize grid generator
        
        Args:
            midprice: Center price for the grid
            grid_distance: Distance between grid levels
            grid_range: Total range of the grid (up and down from midprice)
        """
        self.midprice = midprice
        self.grid_distance = grid_distance
        self.grid_range = grid_range
        self.grid_levels = self._generate_grid()
        
    def _generate_grid(self) -> np.ndarray:
        """Generate symmetric grid levels around midprice"""
        start = self.midprice - self.grid_range
        end = self.midprice + self.grid_range
        grid = np.arange(start, end + self.grid_distance, self.grid_distance)
        
        # Limit number of grid levels for performance (max 1000)
        if len(grid) > 1000:
            logger.warning(f"Grid has {len(grid)} levels (>1000). Consider increasing grid_distance or reducing grid_range.")
            # Keep only every nth level to reduce to ~500 levels
            step = max(1, len(grid) // 500)
            grid = grid[::step]
            
        logger.info(f"Generated grid with {len(grid)} levels from {start:.4f} to {end:.4f}")
        return grid
    
    def get_grid_levels(self) -> np.ndarray:
        """Return grid levels"""
        return self.grid_levels
    
    def update_midprice(self, new_midprice: float):
        """Update midprice and regenerate grid"""
        self.midprice = new_midprice
        self.grid_levels = self._generate_grid()
        logger.info(f"Updated grid with new midprice: {new_midprice:.4f}")


class GridSignalGenerator:
    """Generates trading signals based on grid crossings"""
    
    def __init__(self, grid_levels: np.ndarray):
        """
        Initialize signal generator
        
        Args:
            grid_levels: Array of grid price levels
        """
        self.grid_levels = grid_levels
        
    def generate_signals(self, data: pd.DataFrame) -> List[int]:
        """
        Generate trading signals when price crosses grid levels
        
        Args:
            data: OHLCV dataframe
            
        Returns:
            List[int]: Signal array (1 for signal, 0 for no signal)
        """
        signals = [0] * len(data)
        
        for i, (index, row) in enumerate(data.iterrows()):
            # Check if any grid level is crossed by the candle
            candle_low = min(row.Low, row.High)
            candle_high = max(row.Low, row.High)
            
            for grid_level in self.grid_levels:
                if candle_low <= grid_level <= candle_high:
                    signals[i] = 1
                    break  # One signal per candle is enough
                    
        logger.info(f"Generated {sum(signals)} signals out of {len(signals)} candles")
        return signals
    
    def add_signals_to_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add signals to the dataframe
        
        Args:
            data: OHLCV dataframe
            
        Returns:
            pd.DataFrame: Data with signals column
        """
        df = data.copy()
        df['signal'] = self.generate_signals(df)
        return df


class GridTradingStrategy:
    """Complete Grid Trading Strategy"""
    
    def __init__(self, 
                 midprice: float,
                 grid_distance: float, 
                 grid_range: float,
                 atr_multiplier: float = 1.5,
                 tp_sl_ratio: float = 0.5):
        """
        Initialize Grid Trading Strategy
        
        Args:
            midprice: Center price for the grid
            grid_distance: Distance between grid levels
            grid_range: Total range of the grid
            atr_multiplier: Multiplier for ATR-based stop loss
            tp_sl_ratio: Take profit to stop loss ratio
        """
        self.grid_generator = GridGenerator(midprice, grid_distance, grid_range)
        self.signal_generator = GridSignalGenerator(self.grid_generator.get_grid_levels())
        self.atr_multiplier = atr_multiplier
        self.tp_sl_ratio = tp_sl_ratio
        
    def prepare_data(self, data: pd.DataFrame, use_dynamic_midprice: bool = False) -> pd.DataFrame:
        """
        Prepare data with signals and indicators
        
        Args:
            data: OHLCV dataframe with technical indicators
            use_dynamic_midprice: Whether to update midprice dynamically
            
        Returns:
            pd.DataFrame: Prepared data with signals
        """
        df = data.copy()
        
        # Update midprice if dynamic pricing is enabled
        if use_dynamic_midprice and 'MA_20' in df.columns:
            new_midprice = df['MA_20'].iloc[-1]
            self.grid_generator.update_midprice(new_midprice)
            self.signal_generator = GridSignalGenerator(self.grid_generator.get_grid_levels())
        
        # Add signals
        df = self.signal_generator.add_signals_to_data(df)
        
        return df
    
    def get_strategy_parameters(self) -> dict:
        """Return strategy parameters for reporting"""
        return {
            'midprice': self.grid_generator.midprice,
            'grid_distance': self.grid_generator.grid_distance,
            'grid_range': self.grid_generator.grid_range,
            'grid_levels_count': len(self.grid_generator.grid_levels),
            'atr_multiplier': self.atr_multiplier,
            'tp_sl_ratio': self.tp_sl_ratio
        }
    
    def get_grid_info(self) -> dict:
        """Return grid information for visualization"""
        return {
            'levels': self.grid_generator.get_grid_levels().tolist(),
            'midprice': self.grid_generator.midprice,
            'range': self.grid_generator.grid_range,
            'distance': self.grid_generator.grid_distance
        }
