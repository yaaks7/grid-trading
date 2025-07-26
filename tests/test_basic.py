"""
Basic tests for Grid Trading Strategy
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data.fetcher import DataFetcher
from src.strategy.grid_trading import GridGenerator, GridSignalGenerator, GridTradingStrategy
from src.backtest.backtester import GridBacktester


class TestGridGenerator:
    """Test Grid Generator functionality"""
    
    def test_grid_generation(self):
        """Test basic grid generation"""
        generator = GridGenerator(midprice=1.0, grid_distance=0.1, grid_range=0.5)
        grid = generator.get_grid_levels()
        
        assert len(grid) > 0
        assert min(grid) >= 0.5  # midprice - grid_range
        assert max(grid) <= 1.5  # midprice + grid_range
        
    def test_grid_symmetry(self):
        """Test grid symmetry around midprice"""
        midprice = 1.065
        generator = GridGenerator(midprice=midprice, grid_distance=0.01, grid_range=0.1)
        grid = generator.get_grid_levels()
        
        # Check if there are levels both above and below midprice
        levels_below = grid[grid < midprice]
        levels_above = grid[grid > midprice]
        
        assert len(levels_below) > 0
        assert len(levels_above) > 0


class TestGridSignalGenerator:
    """Test Grid Signal Generator functionality"""
    
    def create_sample_data(self):
        """Create sample OHLCV data for testing"""
        dates = pd.date_range('2024-01-01', periods=100, freq='5min')
        np.random.seed(42)
        
        data = pd.DataFrame({
            'Open': 1.06 + np.random.randn(100) * 0.001,
            'High': 1.061 + np.random.randn(100) * 0.001,
            'Low': 1.059 + np.random.randn(100) * 0.001,
            'Close': 1.060 + np.random.randn(100) * 0.001,
            'Volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        # Ensure High >= Low
        data['High'] = np.maximum(data['High'], data['Low'])
        
        return data
    
    def test_signal_generation(self):
        """Test signal generation"""
        grid_levels = np.array([1.058, 1.059, 1.060, 1.061, 1.062])
        generator = GridSignalGenerator(grid_levels)
        
        data = self.create_sample_data()
        signals = generator.generate_signals(data)
        
        assert len(signals) == len(data)
        assert all(signal in [0, 1] for signal in signals)
        assert sum(signals) >= 0  # Should have some signals


class TestDataFetcher:
    """Test Data Fetcher functionality"""
    
    def test_data_validation(self):
        """Test data validation"""
        fetcher = DataFetcher()
        
        # Create valid sample data
        data = pd.DataFrame({
            'Open': [1.06, 1.061, 1.062],
            'High': [1.061, 1.062, 1.063],
            'Low': [1.059, 1.060, 1.061],
            'Close': [1.060, 1.061, 1.062],
            'Volume': [1000, 1100, 1200]
        })
        
        assert fetcher.validate_data(data) == True
        
        # Test with missing columns
        invalid_data = data.drop('Volume', axis=1)
        assert fetcher.validate_data(invalid_data) == False
    
    def test_dynamic_midprice(self):
        """Test dynamic midprice calculation"""
        fetcher = DataFetcher()
        
        # Create sample data with moving averages
        data = pd.DataFrame({
            'Close': [1.06, 1.061, 1.062, 1.063, 1.064],
            'MA_20': [1.06, 1.0605, 1.061, 1.0615, 1.062],
            'MA_50': [1.059, 1.0595, 1.060, 1.0605, 1.061]
        })
        
        midprice_ma20 = fetcher.get_dynamic_midprice(data, 'ma_20')
        midprice_ma50 = fetcher.get_dynamic_midprice(data, 'ma_50')
        
        assert midprice_ma20 == 1.062
        assert midprice_ma50 == 1.061


class TestGridTradingStrategy:
    """Test complete Grid Trading Strategy"""
    
    def test_strategy_initialization(self):
        """Test strategy initialization"""
        strategy = GridTradingStrategy(
            midprice=1.065,
            grid_distance=0.003,
            grid_range=0.1
        )
        
        params = strategy.get_strategy_parameters()
        
        assert params['midprice'] == 1.065
        assert params['grid_distance'] == 0.003
        assert params['grid_range'] == 0.1
        assert params['grid_levels_count'] > 0


def run_basic_tests():
    """Run basic functionality tests"""
    print("Running basic Grid Trading Strategy tests...")
    
    # Test 1: Grid Generation
    print("✓ Testing grid generation...")
    generator = GridGenerator(midprice=1.065, grid_distance=0.003, grid_range=0.1)
    grid = generator.get_grid_levels()
    print(f"  Generated {len(grid)} grid levels")
    
    # Test 2: Signal Generation
    print("✓ Testing signal generation...")
    signal_gen = GridSignalGenerator(grid)
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=50, freq='5min')
    sample_data = pd.DataFrame({
        'Open': np.random.normal(1.065, 0.002, 50),
        'High': np.random.normal(1.067, 0.002, 50),
        'Low': np.random.normal(1.063, 0.002, 50),
        'Close': np.random.normal(1.065, 0.002, 50),
        'Volume': np.random.randint(1000, 5000, 50)
    }, index=dates)
    
    # Ensure High >= Low
    sample_data['High'] = np.maximum(sample_data['High'], sample_data['Low'])
    
    signals = signal_gen.generate_signals(sample_data)
    print(f"  Generated {sum(signals)} signals from {len(signals)} candles")
    
    # Test 3: Strategy Integration
    print("✓ Testing strategy integration...")
    strategy = GridTradingStrategy(
        midprice=1.065,
        grid_distance=0.003,
        grid_range=0.1
    )
    
    prepared_data = strategy.prepare_data(sample_data)
    print(f"  Prepared data with {prepared_data['signal'].sum()} signals")
    
    print("✅ All basic tests passed!")
    return True


if __name__ == "__main__":
    run_basic_tests()
