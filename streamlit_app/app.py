"""
Streamlit application for Grid Trading Strategy Backtester
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from data.fetcher import DataFetcher
from strategy.grid_trading import GridTradingStrategy
from backtest.backtester import GridBacktester
from visualization.charts import GridTradingVisualizer, display_metrics_cards, display_strategy_parameters
from settings import SUPPORTED_ASSETS, TradingConfig, DataConfig, STREAMLIT_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
)


def main():
    """Main Streamlit application"""
    
    st.title("📈 Grid Trading Strategy Backtester")
    st.markdown("---")
    
    # Initialize session state for workflow
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'prepared_data' not in st.session_state:
        st.session_state.prepared_data = None
    if 'strategy' not in st.session_state:
        st.session_state.strategy = None
    if 'data_fetcher' not in st.session_state:
        st.session_state.data_fetcher = None
    
    # Progress indicator
    progress_col1, progress_col2 = st.columns(2)
    with progress_col1:
        if st.session_state.step >= 1:
            st.success("✅ 1. Data & Grid Configuration")
        else:
            st.info("⏳ 1. Data & Grid Configuration")
    
    with progress_col2:
        if st.session_state.step >= 2:
            st.success("✅ 2. Backtesting & Risk Management")
        else:
            st.info("⏳ 2. Backtesting & Risk Management")
    
    st.markdown("---")
    
    # STEP 1: Data Loading and Grid Configuration
    if st.session_state.step == 1:
        st.header("📊 Step 1: Data Loading & Grid Configuration")
        st.markdown("Configure your asset, time period, and grid parameters to visualize the trading signals.")
        
        # Sidebar for Step 1 parameters
        with st.sidebar:
            st.header("⚙️ Data & Grid Configuration")
            
            # Asset selection
            st.subheader("📈 Asset Selection")
            selected_symbol = st.selectbox(
                "Choose Asset:",
                options=list(SUPPORTED_ASSETS.keys()),
                format_func=lambda x: f"{SUPPORTED_ASSETS[x]['name']} ({x})"
            )
            
            asset_info = SUPPORTED_ASSETS[selected_symbol]
            
            # Date range
            st.subheader("📅 Date Range")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date:",
                    value=datetime.strptime("2024-01-01", "%Y-%m-%d").date(),
                    max_value=datetime.now().date()
                )
            with col2:
                end_date = st.date_input(
                    "End Date:",
                    value=datetime.strptime("2024-12-31", "%Y-%m-%d").date(),
                    max_value=datetime.now().date()
                )
            
            interval = st.selectbox(
                "Data Interval:",
                options=['1d', '1h', '5m', '15m', '30m'],
                index=0,  # Default to daily
                help="Daily data is recommended for longer backtests"
            )
            
            # Grid parameters
            st.subheader("🎯 Grid Configuration")
            
            use_dynamic_midprice = st.checkbox(
                "Use Dynamic Midprice (MA-20)",
                value=False,
                help="Use 20-period moving average instead of fixed midprice"
            )
            
            if not use_dynamic_midprice:
                midprice = st.number_input(
                    "Midprice:",
                    value=float(asset_info['midprice']),
                    min_value=0.0,
                    step=0.001,
                    format="%.6f",
                    help="Center price around which the grid is built"
                )
            else:
                midprice = asset_info['midprice']  # Will be updated dynamically
                st.info(f"Dynamic midprice will be calculated from data (preview: ~{asset_info['midprice']})")
            
            grid_distance = st.number_input(
                "Grid Distance:",
                value=float(asset_info['grid_distance']),
                min_value=0.0001,
                step=0.0001,
                format="%.6f",
                help="Distance between grid levels"
            )
            
            # Calculate appropriate max_value based on asset type
            default_grid_range = float(asset_info.get('grid_range', 50.0))
            max_grid_range = max(100000.0, default_grid_range * 5)  # At least 5x the default or 100k
            
            grid_range = st.number_input(
                "Grid Range:",
                value=default_grid_range,
                min_value=0.001,
                max_value=max_grid_range,
                step=0.001,
                format="%.6f",
                help="Total range of the grid (up and down from midprice)"
            )
            
            # Grid validation warning
            estimated_levels = int((2 * grid_range) / grid_distance)
            if estimated_levels > 1000:
                st.error(f"⚠️ Warning: This configuration will generate ~{estimated_levels:,} grid levels. "
                        f"This may cause performance issues. Consider:")
                st.markdown("- Increasing Grid Distance (fewer levels)")
                st.markdown("- Reducing Grid Range (smaller area)")
                st.markdown("- Recommended: < 1000 levels for optimal performance")
            elif estimated_levels > 500:
                st.warning(f"⚠️ This will generate ~{estimated_levels:,} grid levels. "
                          f"Consider adjusting parameters for better performance.")
            else:
                st.success(f"✅ Grid will have ~{estimated_levels:,} levels (optimal range)")
            
            # Load data and generate grid button
            load_data_btn = st.button("📊 Load Data & Generate Grid", type="primary")
        
        # Main area for Step 1
        if load_data_btn:
            with st.spinner("Loading data and generating grid..."):
                try:
                    # Initialize components
                    st.session_state.data_fetcher = DataFetcher()
                    visualizer = GridTradingVisualizer()
                    
                    # Fetch data
                    st.info(f"Fetching {asset_info['name']} data...")
                    raw_data = st.session_state.data_fetcher.fetch_data(
                        symbol=selected_symbol,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                        interval=interval
                    )
                    
                    # Add technical indicators
                    data_with_indicators = st.session_state.data_fetcher.add_technical_indicators(raw_data)
                    
                    # Get dynamic midprice if enabled
                    if use_dynamic_midprice:
                        midprice = st.session_state.data_fetcher.get_dynamic_midprice(data_with_indicators)
                        st.success(f"Dynamic midprice calculated: {midprice:.6f}")
                    
                    # Initialize strategy
                    st.session_state.strategy = GridTradingStrategy(
                        midprice=midprice,
                        grid_distance=grid_distance,
                        grid_range=grid_range
                    )
                    
                    # Prepare data with signals
                    st.session_state.prepared_data = st.session_state.strategy.prepare_data(
                        data_with_indicators, 
                        use_dynamic_midprice=use_dynamic_midprice
                    )
                    
                    st.success("✅ Data loaded and grid generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error loading data: {str(e)}")
                    return
        
        # Display results if data is loaded
        if st.session_state.prepared_data is not None and st.session_state.strategy is not None:
            
            # Data summary
            data_summary = st.session_state.data_fetcher.get_data_summary(st.session_state.prepared_data)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Data Points", data_summary['rows'])
            with col2:
                st.metric("Price Range", f"{data_summary['price_range']['min']:.2f} - {data_summary['price_range']['max']:.2f}")
            with col3:
                st.metric("Current Price", f"{data_summary['price_range']['current']:.2f}")
            with col4:
                st.metric("Trading Signals", st.session_state.prepared_data['signal'].sum())
            
            # Strategy parameters
            strategy_info = st.session_state.strategy.get_strategy_parameters()
            with st.expander("📋 Grid Configuration Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Midprice:** {strategy_info['midprice']}")
                    st.write(f"**Grid Distance:** {strategy_info['grid_distance']}")
                    st.write(f"**Grid Range:** {strategy_info['grid_range']}")
                with col2:
                    st.write(f"**Grid Levels:** {strategy_info['grid_levels_count']}")
                    st.write(f"**Signals Generated:** {st.session_state.prepared_data['signal'].sum()}")
                    grid_info = st.session_state.strategy.get_grid_info()
                    st.write(f"**Level Range:** {min(grid_info['levels']):.4f} - {max(grid_info['levels']):.4f}")
            
            # Price chart with grid and signals
            st.subheader("📈 Price Chart with Grid Levels & Trading Signals")
            
            visualizer = GridTradingVisualizer()
            grid_info = st.session_state.strategy.get_grid_info()
            price_chart = visualizer.plot_price_with_grid(
                st.session_state.prepared_data,
                grid_info['levels'],
                f"{asset_info['name']} Price with Grid Levels"
            )
            st.plotly_chart(price_chart, use_container_width=True)
            
            # Signal analysis
            signals_count = st.session_state.prepared_data['signal'].sum()
            total_candles = len(st.session_state.prepared_data)
            signal_frequency = (signals_count / total_candles * 100) if total_candles > 0 else 0
            
            st.info(f"📊 **Signal Analysis**: {signals_count} trading signals generated out of {total_candles} candles ({signal_frequency:.1f}% frequency)")
            
            if signals_count > 0:
                st.success("✅ Grid configuration looks good! You can proceed to backtesting.")
                if st.button("➡️ Proceed to Backtesting Configuration", type="primary"):
                    st.session_state.step = 2
                    st.rerun()
            else:
                st.warning("⚠️ No trading signals generated. Consider adjusting your grid parameters:")
                st.write("- **Increase grid range** if price is outside the grid")
                st.write("- **Decrease grid distance** for more levels")
                st.write("- **Adjust midprice** to center it on the price range")
            
            # Allow parameter adjustment
            if st.button("🔄 Adjust Grid Parameters"):
                st.session_state.prepared_data = None
                st.session_state.strategy = None
                st.rerun()
    
    # STEP 2: Backtesting Configuration
    elif st.session_state.step == 2:
        st.header("⚙️ Step 2: Backtesting & Risk Management")
        st.markdown("Configure your backtesting parameters and risk management rules.")
        
        if st.session_state.prepared_data is None:
            st.error("❌ No data loaded. Please go back to Step 1.")
            if st.button("⬅️ Back to Data Configuration"):
                st.session_state.step = 1
                st.rerun()
            return
        
        # Sidebar for Step 2 parameters
        with st.sidebar:
            st.header("⚙️ Backtesting Configuration")
            
            # Portfolio settings
            st.subheader("💰 Portfolio Settings")
            cash = st.number_input(
                "Initial Cash:",
                value=10000,
                min_value=1000,
                max_value=1000000,
                step=1000,
                help="Starting capital for backtesting"
            )
            
            position_size = st.number_input(
                "Position Size:",
                value=100,
                min_value=1,
                max_value=1000,
                step=10,
                help="Number of shares/units per trade"
            )
            
            max_trades = st.number_input(
                "Max Concurrent Trades:",
                value=5,
                min_value=1,
                max_value=20,
                step=1,
                help="Maximum number of simultaneous positions"
            )
            
            # Risk management
            st.subheader("🛡️ Risk Management")
            atr_multiplier = st.slider(
                "ATR Multiplier (Stop Loss):",
                min_value=0.5,
                max_value=5.0,
                value=1.5,
                step=0.1,
                help="Stop loss distance as multiple of ATR"
            )
            
            tp_sl_ratio = st.slider(
                "Take Profit / Stop Loss Ratio:",
                min_value=0.1,
                max_value=3.0,
                value=0.5,
                step=0.1,
                help="Take profit distance relative to stop loss"
            )
            
            # Advanced settings
            st.subheader("⚙️ Advanced Settings")
            margin = st.number_input(
                "Margin Requirement:",
                value=0.01,
                min_value=0.001,
                max_value=1.0,
                step=0.001,
                format="%.3f",
                help="Margin requirement (0.01 = 1%)"
            )
            
            commission = st.number_input(
                "Commission per Trade:",
                value=0.001,
                min_value=0.0,
                max_value=0.01,
                step=0.0001,
                format="%.4f",
                help="Commission as fraction of trade value"
            )
            
            # Run backtest button
            run_backtest = st.button("🚀 Run Backtest", type="primary")
        
        # Main area for Step 2
        # Show summary of Step 1 configuration
        with st.expander("📋 Grid Configuration Summary (Step 1)", expanded=False):
            strategy_info = st.session_state.strategy.get_strategy_parameters()
            data_summary = st.session_state.data_fetcher.get_data_summary(st.session_state.prepared_data)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Data:**")
                st.write(f"• Points: {data_summary['rows']}")
                st.write(f"• Signals: {st.session_state.prepared_data['signal'].sum()}")
            with col2:
                st.write("**Grid:**")
                st.write(f"• Midprice: {strategy_info['midprice']}")
                st.write(f"• Distance: {strategy_info['grid_distance']}")
                st.write(f"• Levels: {strategy_info['grid_levels_count']}")
            with col3:
                st.write("**Price Range:**")
                st.write(f"• Min: {data_summary['price_range']['min']:.2f}")
                st.write(f"• Max: {data_summary['price_range']['max']:.2f}")
                st.write(f"• Current: {data_summary['price_range']['current']:.2f}")
        
        # Backtesting preview
        st.subheader("🎯 Backtesting Configuration Preview")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Portfolio Settings:**")
            st.write(f"• Initial Cash: ${cash:,}")
            st.write(f"• Position Size: {position_size} units")
            st.write(f"• Max Trades: {max_trades}")
            st.write(f"• Margin: {margin*100:.1f}%")
        
        with col2:
            st.write("**Risk Management:**")
            st.write(f"• ATR Multiplier: {atr_multiplier}x")
            st.write(f"• TP/SL Ratio: {tp_sl_ratio}")
            st.write(f"• Commission: {commission*100:.2f}%")
            
            # Calculate approximate risk per trade
            strategy_info = st.session_state.strategy.get_strategy_parameters()
            approx_sl = strategy_info['grid_distance'] * atr_multiplier
            risk_per_trade = position_size * approx_sl
            st.write(f"• Est. Risk/Trade: ${risk_per_trade:.2f}")
        
        # Risk warnings
        total_risk = max_trades * position_size * strategy_info['grid_distance'] * atr_multiplier
        if total_risk > cash * 0.1:  # More than 10% of capital at risk
            st.warning(f"⚠️ **High Risk Warning**: Total potential loss (${total_risk:.2f}) exceeds 10% of capital")
        
        if position_size * strategy_info['midprice'] > cash * 0.2:  # Single position > 20% of capital
            st.warning(f"⚠️ **Position Size Warning**: Single position value exceeds 20% of capital")
        
        # Run backtest
        if run_backtest:
            with st.spinner("Running backtest..."):
                try:
                    # Strategy parameters for backtesting
                    strategy_params = {
                        'position_size': position_size,
                        'atr_multiplier': atr_multiplier,
                        'tp_sl_ratio': tp_sl_ratio,
                        'max_trades': max_trades,
                        'grid_distance': strategy_info['grid_distance']
                    }
                    
                    backtester = GridBacktester(cash=cash, margin=margin)
                    results = backtester.run_backtest(st.session_state.prepared_data, strategy_params)
                    
                    st.success("✅ Backtest completed successfully!")
                    
                    # Display results immediately after backtest
                    display_backtest_results(backtester, st.session_state.data_fetcher, st.session_state.strategy)
                    
                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Grid Configuration"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("🔄 New Analysis"):
                # Reset all session state
                st.session_state.step = 1
                st.session_state.prepared_data = None
                st.session_state.strategy = None
                st.session_state.data_fetcher = None
                st.rerun()


def display_backtest_results(backtester, data_fetcher, strategy):
    """Display comprehensive backtest results"""
    
    st.header("📊 Backtest Results")
    
    # Performance metrics
    metrics = backtester.get_performance_metrics()
    display_metrics_cards(metrics)
    
    # Charts
    st.subheader("📈 Performance Charts")
    
    visualizer = GridTradingVisualizer()
    
    # Equity curve
    equity_data = backtester.get_equity_curve()
    equity_chart = visualizer.plot_equity_curve(equity_data)
    st.plotly_chart(equity_chart, use_container_width=True)
    
    # Drawdown chart
    drawdown_chart = visualizer.plot_drawdown(equity_data)
    st.plotly_chart(drawdown_chart, use_container_width=True)
    
    # Performance summary chart
    performance_chart = visualizer.create_performance_summary_chart(metrics)
    st.plotly_chart(performance_chart, use_container_width=True)
    
    # Trade analysis
    trades_df = backtester.get_trades_dataframe()
    if not trades_df.empty:
        with st.expander("📋 Detailed Trade Analysis"):
            st.subheader("Trade Statistics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Winning Trades:**")
                winning_trades = trades_df[trades_df['ReturnPct'] > 0]
                if not winning_trades.empty:
                    st.write(f"• Count: {len(winning_trades)}")
                    st.write(f"• Average: {winning_trades['ReturnPct'].mean():.2f}%")
                    st.write(f"• Best: {winning_trades['ReturnPct'].max():.2f}%")
            
            with col2:
                st.write("**Losing Trades:**")
                losing_trades = trades_df[trades_df['ReturnPct'] < 0]
                if not losing_trades.empty:
                    st.write(f"• Count: {len(losing_trades)}")
                    st.write(f"• Average: {losing_trades['ReturnPct'].mean():.2f}%")
                    st.write(f"• Worst: {losing_trades['ReturnPct'].min():.2f}%")
            
            st.subheader("Trade Details")
            st.dataframe(trades_df, use_container_width=True)
            
            # Trade distribution
            trade_dist_chart = visualizer.create_trade_distribution_chart(trades_df)
            st.plotly_chart(trade_dist_chart, use_container_width=True)
    
    # Download results
    st.subheader("💾 Download Results")
    col1, col2 = st.columns(2)
    
    with col1:
        # Prepare data for download
        results_csv = st.session_state.prepared_data.to_csv()
        st.download_button(
            label="📥 Download Price Data with Signals",
            data=results_csv,
            file_name=f"grid_trading_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        if not trades_df.empty:
            trades_csv = trades_df.to_csv()
            st.download_button(
                label="📥 Download Trade Details",
                data=trades_csv,
                file_name=f"grid_trading_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
