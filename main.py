#!/usr/bin/env python3
"""
Grid Trading Strategy - CLI Interface

A  grid trading backtesting system.
This script provides a command-line interface for running backtests on various assets.

Usage:
    python main.py [--asset ASSET] [--start START_DATE] [--end END_DATE]

Examples:
    python main.py                           # Run with default settings (AAPL)
    python main.py --asset BTC-USD           # Test Bitcoin
    python main.py --asset EURUSD=X --start 2024-06-01  # EUR/USD with custom date

Author: Yanis Aksas
Portfolio: https://github.com/yaaks7/grid-trading
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
import pandas as pd

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.fetcher import DataFetcher
from src.strategy.grid_trading import GridTradingStrategy
from src.backtest.backtester import GridBacktester
from src.visualization.charts import GridTradingVisualizer
from config.settings import SUPPORTED_ASSETS, TradingConfig, DataConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Grid Trading Strategy Backtester',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Default: AAPL, 2024 data
  %(prog)s --asset BTC-USD                    # Bitcoin backtest
  %(prog)s --asset EURUSD=X --dynamic        # EUR/USD with dynamic midprice
  %(prog)s --start 2024-06-01 --end 2024-12-31  # Custom date range
        """
    )
    
    parser.add_argument(
        '--asset', 
        default='AAPL',
        choices=list(SUPPORTED_ASSETS.keys()),
        help='Asset to backtest (default: AAPL)'
    )
    
    parser.add_argument(
        '--start',
        default='2024-01-01',
        help='Start date (YYYY-MM-DD, default: 2024-01-01)'
    )
    
    parser.add_argument(
        '--end',
        default='2024-12-31',
        help='End date (YYYY-MM-DD, default: 2024-12-31)'
    )
    
    parser.add_argument(
        '--dynamic',
        action='store_true',
        help='Use dynamic midprice (MA-20) instead of static'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data/results',
        help='Output directory for results (default: data/results)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def save_results(results, metrics, symbol, start_date, end_date, output_dir):
    """Save backtest results to files"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"grid_trading_{symbol}_{start_date}_{end_date}_{timestamp}"
    
    # Save detailed results to CSV
    csv_file = os.path.join(output_dir, f"{base_filename}_results.csv")
    results.to_csv(csv_file, index=True)
    
    # Save metrics to JSON
    import json
    metrics_file = os.path.join(output_dir, f"{base_filename}_metrics.json")
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    print(f"✅ Results saved to:")
    print(f"   📊 Details: {csv_file}")
    print(f"   📈 Metrics: {metrics_file}")
    
    return csv_file, metrics_file


def main():
    """Main execution function"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get asset configuration
    if args.asset not in SUPPORTED_ASSETS:
        print(f"❌ Error: Asset {args.asset} not supported")
        print(f"Available assets: {', '.join(SUPPORTED_ASSETS.keys())}")
        return 1
    
    asset_info = SUPPORTED_ASSETS[args.asset]
    
    print("🚀 Grid Trading Strategy - Professional Backtester")
    print("=" * 55)
    print(f"📊 Asset: {asset_info['name']} ({args.asset})")
    print(f"📅 Period: {args.start} to {args.end}")
    print(f"🎯 Midprice: {'Dynamic (MA-20)' if args.dynamic else 'Static'}")
    print(f"📁 Output: {args.output_dir}")
    
    try:
        # Step 1: Fetch and prepare data
        print("\n1️⃣ Fetching market data...")
        data_fetcher = DataFetcher()
        
        raw_data = data_fetcher.fetch_data(
            symbol=args.asset,
            start_date=args.start,
            end_date=args.end,
            interval='1d'
        )
        
        data_with_indicators = data_fetcher.add_technical_indicators(raw_data)
        print(f"✅ Fetched {len(data_with_indicators)} data points")
        
        # Step 2: Initialize strategy
        print("\n2️⃣ Configuring strategy...")
        
        if args.dynamic:
            midprice = data_fetcher.get_dynamic_midprice(data_with_indicators)
            print(f"📊 Dynamic midprice: {midprice:.4f}")
        else:
            midprice = asset_info['midprice']
            print(f"📊 Static midprice: {midprice:.4f}")
        
        strategy = GridTradingStrategy(
            midprice=midprice,
            grid_distance=asset_info['grid_distance'],
            grid_range=asset_info['grid_range']
        )
        
        prepared_data = strategy.prepare_data(data_with_indicators)
        signals_count = prepared_data['signal'].sum()
        
        strategy_params = strategy.get_strategy_parameters()
        print(f"✅ Grid configured: {strategy_params['grid_levels_count']} levels")
        print(f"   Range: {strategy_params['grid_range']:.4f}")
        print(f"   Distance: {strategy_params['grid_distance']:.4f}")
        print(f"   Signals: {signals_count}/{len(prepared_data)} ({signals_count/len(prepared_data)*100:.1f}%)")
        
        # Step 3: Run backtest
        print("\n3️⃣ Running backtest...")
        
        trading_config = TradingConfig()
        backtester = GridBacktester(
            cash=trading_config.cash,
            margin=trading_config.margin
        )
        
        backtest_params = {
            'position_size': trading_config.position_size,
            'atr_multiplier': trading_config.atr_multiplier,
            'tp_sl_ratio': trading_config.tp_sl_ratio,
            'max_trades': trading_config.max_trades,
            'grid_distance': asset_info['grid_distance']
        }
        
        results = backtester.run_backtest(prepared_data, backtest_params)
        metrics = backtester.get_performance_metrics()
        
        print("✅ Backtest completed")
        
        # Step 4: Display results
        print("\n4️⃣ Performance Summary")
        print("=" * 30)
        
        # Extract numeric values for better formatting
        total_return = metrics.get('total_return_value', 0)
        sharpe_ratio = metrics.get('sharpe_ratio_value', 0)
        max_drawdown = metrics.get('max_drawdown_value', 0)
        win_rate = metrics.get('win_rate_value', 0)
        total_trades = metrics.get('total_trades', 0)
        
        print(f"📈 Total Return: {total_return:.2f}%")
        print(f"📊 Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"📉 Max Drawdown: {max_drawdown:.2f}%")
        print(f"🎯 Win Rate: {win_rate:.1f}%")
        print(f"🔢 Total Trades: {total_trades}")
        
        # Step 5: Save results
        print("\n5️⃣ Saving results...")
        csv_file, metrics_file = save_results(
            results, metrics, args.asset, args.start, args.end, args.output_dir
        )
        
        # Step 6: Generate chart
        print("\n6️⃣ Generating visualization...")
        try:
            visualizer = GridTradingVisualizer()
            grid_levels = strategy.grid_generator.get_grid_levels()
            
            fig = visualizer.plot_price_with_grid(
                data=prepared_data,
                grid_levels=grid_levels,
                title=f"{asset_info['name']} - Grid Trading Analysis"
            )
            
            chart_file = os.path.join(args.output_dir, f"chart_{args.asset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            fig.write_html(chart_file)
            print(f"✅ Chart saved: {chart_file}")
            
        except Exception as e:
            print(f"⚠️ Chart generation failed: {e}")
        
        print("\n🎉 Analysis complete!")
        print(f"💡 Open {csv_file} to see detailed results")
        print(f"🖥️ Run 'streamlit run streamlit_app/app.py' for interactive analysis")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
