"""
Backtesting module for Grid Trading Strategy
"""

import pandas as pd
import numpy as np
from backtesting import Strategy, Backtest
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GridTradingBacktestStrategy(Strategy):
    """Backtesting strategy implementation using backtesting.py"""
    
    # Strategy parameters
    mysize = 50
    atr_multiplier = 1.5
    tp_sl_ratio = 0.5
    max_trades = 3
    grid_distance = 0.003
    
    def init(self):
        """Initialize strategy"""
        super().init()
        # Create signal indicator
        self.signal1 = self.I(lambda: self.data.signal)
        
    def next(self):
        """Execute strategy logic for each bar"""
        super().next()
        
        # Calculate stop loss and take profit levels
        slatr = self.atr_multiplier * self.grid_distance
        
        # Check for signal and position limits
        if self.signal1[-1] == 1 and len(self.trades) <= self.max_trades:
            
            current_price = self.data.Close[-1]
            
            # Place sell order (short)
            sl_short = current_price + slatr
            tp_short = current_price - slatr * self.tp_sl_ratio
            self.sell(sl=sl_short, tp=tp_short, size=self.mysize)
            
            # Place buy order (long)
            sl_long = current_price - slatr
            tp_long = current_price + slatr * self.tp_sl_ratio
            self.buy(sl=sl_long, tp=tp_long, size=self.mysize)


class GridBacktester:
    """Main backtesting class for Grid Trading Strategy"""
    
    def __init__(self, 
                 cash: float = 50,
                 margin: float = 0.01,
                 hedging: bool = True,
                 exclusive_orders: bool = False):
        """
        Initialize backtester
        
        Args:
            cash: Initial cash amount
            margin: Margin requirement (1/100 = 1% margin)
            hedging: Allow hedging positions
            exclusive_orders: Whether orders are exclusive
        """
        self.cash = cash
        self.margin = margin
        self.hedging = hedging
        self.exclusive_orders = exclusive_orders
        self.backtest_results = None
        
    def run_backtest(self, 
                    data: pd.DataFrame, 
                    strategy_params: dict) -> pd.Series:
        """
        Run backtest with given data and parameters
        
        Args:
            data: Prepared dataframe with signals
            strategy_params: Strategy parameters
            
        Returns:
            pd.Series: Backtest results
        """
        # Update strategy parameters
        GridTradingBacktestStrategy.mysize = strategy_params.get('position_size', 50)
        GridTradingBacktestStrategy.atr_multiplier = strategy_params.get('atr_multiplier', 1.5)
        GridTradingBacktestStrategy.tp_sl_ratio = strategy_params.get('tp_sl_ratio', 0.5)
        GridTradingBacktestStrategy.max_trades = strategy_params.get('max_trades', 3)
        GridTradingBacktestStrategy.grid_distance = strategy_params.get('grid_distance', 0.003)
        
        # Create and run backtest
        bt = Backtest(
            data, 
            GridTradingBacktestStrategy,
            cash=self.cash,
            margin=self.margin,
            hedging=self.hedging,
            exclusive_orders=self.exclusive_orders
        )
        
        try:
            results = bt.run()
            self.backtest_results = results
            self.backtest_object = bt
            
            logger.info("Backtest completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Extract key performance metrics from backtest results
        
        Returns:
            Dict: Performance metrics
        """
        if self.backtest_results is None:
            raise ValueError("No backtest results available. Run backtest first.")
        
        results = self.backtest_results
        
        metrics = {
            # Core Performance
            'total_return': f"{results['Return [%]']:.2f}%",
            'total_return_value': results['Return [%]'],
            'annualized_return': f"{results.get('Return (Ann.) [%]', 0):.2f}%",
            'volatility': f"{results.get('Volatility (Ann.) [%]', 0):.2f}%",
            'sharpe_ratio': f"{results.get('Sharpe Ratio', 0):.2f}",
            'calmar_ratio': f"{results.get('Calmar Ratio', 0):.2f}",
            
            # Risk Metrics
            'max_drawdown': f"{results.get('Max. Drawdown [%]', 0):.2f}%",
            'max_drawdown_value': results.get('Max. Drawdown [%]', 0),
            'max_drawdown_duration': results.get('Max. Drawdown Duration', 'N/A'),
            
            # Trading Metrics
            'total_trades': results.get('# Trades', 0),
            'win_rate': f"{results.get('Win Rate [%]', 0):.2f}%",
            'win_rate_value': results.get('Win Rate [%]', 0),
            'best_trade': f"{results.get('Best Trade [%]', 0):.2f}%",
            'worst_trade': f"{results.get('Worst Trade [%]', 0):.2f}%",
            'avg_trade': f"{results.get('Avg. Trade [%]', 0):.2f}%",
            
            # Duration Metrics
            'avg_trade_duration': results.get('Avg. Trade Duration', 'N/A'),
            'max_trade_duration': results.get('Max. Trade Duration', 'N/A'),
            
            # Portfolio Metrics
            'start_equity': results.get('Start', 0),
            'end_equity': results.get('End', 0),
            'equity_peak': results.get('Equity Peak [$]', 0),
            
            # Buy & Hold Comparison
            'buy_hold_return': f"{results.get('Buy & Hold Return [%]', 0):.2f}%",
        }
        
        return metrics
    
    def get_trades_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get trades dataframe from backtest results
        
        Returns:
            pd.DataFrame: Trades dataframe or None
        """
        if self.backtest_results is None:
            return None
            
        return self.backtest_results.get('_trades', pd.DataFrame())
    
    def plot_results(self, **kwargs):
        """
        Plot backtest results
        
        Args:
            **kwargs: Arguments passed to bt.plot()
        """
        if hasattr(self, 'backtest_object'):
            default_kwargs = {
                'show_legend': False,
                'plot_width': None,
                'plot_equity': True,
                'plot_return': False,
                'plot_pl': False,
                'plot_volume': False,
                'plot_drawdown': True,
                'smooth_equity': False,
                'relative_equity': True,
                'superimpose': True,
                'resample': False,
                'reverse_indicators': False,
                'open_browser': False
            }
            default_kwargs.update(kwargs)
            
            return self.backtest_object.plot(**default_kwargs)
        else:
            raise ValueError("No backtest object available for plotting")
    
    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get equity curve data for custom plotting
        
        Returns:
            pd.DataFrame: Equity curve data
        """
        if self.backtest_results is None:
            raise ValueError("No backtest results available")
            
        # Get equity curve from results
        equity_curve = self.backtest_results._equity_curve
        return equity_curve
