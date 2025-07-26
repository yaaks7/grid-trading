#!/usr/bin/env python3
"""
Test script for EUR/USD grid trading with corrected parameters
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.fetcher import DataFetcher
from src.strategy.grid_trading import GridTradingStrategy
from src.visualization.charts import GridTradingVisualizer
from config.settings import SUPPORTED_ASSETS

def test_eurusd_grid():
    """Test EUR/USD with corrected parameters"""
    
    # Configuration for EUR/USD
    asset_info = SUPPORTED_ASSETS['EURUSD=X']
    print(f"🧪 Testing {asset_info['name']} with corrected parameters:")
    print(f"   Midprice: {asset_info['midprice']}")
    print(f"   Grid Distance: {asset_info['grid_distance']}")
    print(f"   Grid Range: {asset_info['grid_range']}")
    
    # Fetch data
    print("\n📊 Fetching EUR/USD data...")
    fetcher = DataFetcher()
    
    try:
        # Use recent data to avoid weekend issues
        data = fetcher.fetch_data(
            symbol='EURUSD=X',
            start_date='2024-06-01',
            end_date='2024-12-31',
            interval='1d'
        )
        
        data_with_indicators = fetcher.add_technical_indicators(data)
        print(f"✅ Fetched {len(data_with_indicators)} data points")
        print(f"   Price range: {data_with_indicators['Close'].min():.4f} - {data_with_indicators['Close'].max():.4f}")
        
        # Test static midprice
        print("\n🎯 Testing with static midprice...")
        strategy_static = GridTradingStrategy(
            midprice=asset_info['midprice'],
            grid_distance=asset_info['grid_distance'],
            grid_range=asset_info['grid_range']
        )
        
        grid_levels = strategy_static.grid_generator.get_grid_levels()
        print(f"   Grid levels: {len(grid_levels)}")
        print(f"   Level range: {grid_levels.min():.4f} - {grid_levels.max():.4f}")
        
        prepared_data_static = strategy_static.prepare_data(data_with_indicators)
        signals_static = prepared_data_static['signal'].sum()
        print(f"   Signals generated: {signals_static}")
        
        # Test dynamic midprice
        print("\n🔄 Testing with dynamic midprice...")
        dynamic_midprice = fetcher.get_dynamic_midprice(data_with_indicators)
        print(f"   Dynamic midprice: {dynamic_midprice:.4f}")
        
        strategy_dynamic = GridTradingStrategy(
            midprice=dynamic_midprice,
            grid_distance=asset_info['grid_distance'],
            grid_range=asset_info['grid_range']
        )
        
        grid_levels_dynamic = strategy_dynamic.grid_generator.get_grid_levels()
        print(f"   Grid levels: {len(grid_levels_dynamic)}")
        print(f"   Level range: {grid_levels_dynamic.min():.4f} - {grid_levels_dynamic.max():.4f}")
        
        prepared_data_dynamic = strategy_dynamic.prepare_data(data_with_indicators)
        signals_dynamic = prepared_data_dynamic['signal'].sum()
        print(f"   Signals generated: {signals_dynamic}")
        
        # Test visualization
        print("\n📈 Testing visualization...")
        visualizer = GridTradingVisualizer()
        
        try:
            fig = visualizer.plot_price_with_grid(
                data=prepared_data_dynamic,
                grid_levels=grid_levels_dynamic,
                title="EUR/USD Test - Grid Trading Signals"
            )
            print("✅ Visualization created successfully")
            print(f"   Chart contains {len(fig.data)} traces")
            
            # Save as HTML for testing
            fig.write_html("test_eurusd_chart.html")
            print("✅ Chart saved as test_eurusd_chart.html")
            
        except Exception as e:
            print(f"❌ Visualization error: {e}")
        
        # Summary
        print("\n📋 Summary:")
        print(f"   Best configuration: {'Dynamic' if signals_dynamic > signals_static else 'Static'} midprice")
        print(f"   Max signals: {max(signals_static, signals_dynamic)}")
        print(f"   Grid efficiency: {max(signals_static, signals_dynamic) / len(data_with_indicators) * 100:.1f}% of candles have signals")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EUR/USD Grid Trading Test")
    print("=" * 40)
    
    success = test_eurusd_grid()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("💡 You can now use EUR/USD in the Streamlit app with confidence.")
    else:
        print("\n❌ Test failed!")
        print("💡 Check the error messages above for troubleshooting.")
