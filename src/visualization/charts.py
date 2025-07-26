"""
Visualization module for Grid Trading Strategy
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import streamlit as st


class GridTradingVisualizer:
    """Visualization class for grid trading analysis"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8',
            'grid': '#cccccc',
            'signal': '#ff00ff'
        }
    
    def plot_price_with_grid(self, 
                           data: pd.DataFrame, 
                           grid_levels: List[float],
                           title: str = "Price Chart with Grid Levels") -> go.Figure:
        """
        Plot price candlestick chart with grid levels
        
        Args:
            data: OHLCV dataframe
            grid_levels: List of grid price levels
            title: Chart title
            
        Returns:
            plotly.graph_objects.Figure: Interactive chart
        """
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            increasing_line_color=self.colors['success'],
            decreasing_line_color=self.colors['danger']
        ))
        
        # Add grid levels (limit display for performance)
        max_grid_display = 100  # Maximum grid lines to display
        if len(grid_levels) > max_grid_display:
            # Display only every nth level to avoid clutter
            step = max(1, len(grid_levels) // max_grid_display)
            display_levels = grid_levels[::step]
            st.info(f"Displaying {len(display_levels)} out of {len(grid_levels)} grid levels for clarity")
        else:
            display_levels = grid_levels
            
        for level in display_levels:
            fig.add_hline(
                y=level, 
                line_dash="dash", 
                line_color=self.colors['grid'],
                line_width=1,
                opacity=0.6
            )
        
        # Add signals if available
        if 'signal' in data.columns:
            signal_points = data[data['signal'] == 1]
            if not signal_points.empty:
                fig.add_trace(go.Scatter(
                    x=signal_points.index,
                    y=signal_points['Close'],
                    mode='markers',
                    marker=dict(
                        color=self.colors['signal'],
                        size=8,
                        symbol='triangle-up'
                    ),
                    name='Trading Signals'
                ))
        
        fig.update_layout(
            title=title,
            yaxis_title='Price',
            xaxis_title='Time',
            template='plotly_white',
            height=600,
            showlegend=True
        )
        
        return fig
    
    def plot_equity_curve(self, 
                         equity_data: pd.DataFrame,
                         title: str = "Equity Curve") -> go.Figure:
        """
        Plot equity curve from backtest results
        
        Args:
            equity_data: Equity curve dataframe
            title: Chart title
            
        Returns:
            plotly.graph_objects.Figure: Equity curve chart
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=equity_data.index,
            y=equity_data['Equity'],
            mode='lines',
            line=dict(color=self.colors['primary'], width=2),
            name='Strategy Equity',
            fill='tonexty'
        ))
        
        # Add buy & hold if available
        if 'EquityB&H' in equity_data.columns:
            fig.add_trace(go.Scatter(
                x=equity_data.index,
                y=equity_data['EquityB&H'],
                mode='lines',
                line=dict(color=self.colors['secondary'], width=2, dash='dash'),
                name='Buy & Hold'
            ))
        
        fig.update_layout(
            title=title,
            yaxis_title='Equity ($)',
            xaxis_title='Time',
            template='plotly_white',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def plot_drawdown(self, 
                     equity_data: pd.DataFrame,
                     title: str = "Drawdown Analysis") -> go.Figure:
        """
        Plot drawdown chart
        
        Args:
            equity_data: Equity curve dataframe
            title: Chart title
            
        Returns:
            plotly.graph_objects.Figure: Drawdown chart
        """
        if 'DrawdownPct' not in equity_data.columns:
            return go.Figure()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=equity_data.index,
            y=equity_data['DrawdownPct'],
            mode='lines',
            line=dict(color=self.colors['danger'], width=2),
            name='Drawdown %',
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title=title,
            yaxis_title='Drawdown (%)',
            xaxis_title='Time',
            template='plotly_white',
            height=300,
            showlegend=True
        )
        
        return fig
    
    def create_performance_summary_chart(self, metrics: Dict) -> go.Figure:
        """
        Create a summary chart of key performance metrics
        
        Args:
            metrics: Performance metrics dictionary
            
        Returns:
            plotly.graph_objects.Figure: Performance summary chart
        """
        # Extract numeric values
        metrics_to_plot = {
            'Total Return': metrics.get('total_return_value', 0),
            'Sharpe Ratio': float(metrics.get('sharpe_ratio', '0').replace('%', '')),
            'Max Drawdown': -abs(metrics.get('max_drawdown_value', 0)),
            'Win Rate': metrics.get('win_rate_value', 0)
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(metrics_to_plot.keys()),
                y=list(metrics_to_plot.values()),
                marker_color=[
                    self.colors['success'] if v > 0 else self.colors['danger'] 
                    for v in metrics_to_plot.values()
                ]
            )
        ])
        
        fig.update_layout(
            title="Key Performance Metrics",
            yaxis_title="Value",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_trade_distribution_chart(self, trades_df: pd.DataFrame) -> go.Figure:
        """
        Create trade distribution chart
        
        Args:
            trades_df: Trades dataframe
            
        Returns:
            plotly.graph_objects.Figure: Trade distribution chart
        """
        if trades_df.empty:
            return go.Figure()
        
        # Calculate return percentages
        returns = trades_df['ReturnPct'].dropna()
        
        fig = go.Figure(data=[
            go.Histogram(
                x=returns,
                nbinsx=20,
                marker_color=self.colors['info'],
                opacity=0.7
            )
        ])
        
        fig.update_layout(
            title="Trade Return Distribution",
            xaxis_title="Return (%)",
            yaxis_title="Frequency",
            template='plotly_white',
            height=400
        )
        
        return fig


def display_metrics_cards(metrics: Dict):
    """
    Display performance metrics as Streamlit cards
    
    Args:
        metrics: Performance metrics dictionary
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Return",
            value=metrics.get('total_return', 'N/A'),
            delta=None
        )
        st.metric(
            label="Sharpe Ratio", 
            value=metrics.get('sharpe_ratio', 'N/A'),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Max Drawdown",
            value=metrics.get('max_drawdown', 'N/A'),
            delta=None
        )
        st.metric(
            label="Win Rate",
            value=metrics.get('win_rate', 'N/A'),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Trades",
            value=metrics.get('total_trades', 'N/A'),
            delta=None
        )
        st.metric(
            label="Best Trade",
            value=metrics.get('best_trade', 'N/A'),
            delta=None
        )
    
    with col4:
        st.metric(
            label="Worst Trade",
            value=metrics.get('worst_trade', 'N/A'),
            delta=None
        )
        st.metric(
            label="Avg Trade",
            value=metrics.get('avg_trade', 'N/A'),
            delta=None
        )


def display_strategy_parameters(params: Dict):
    """
    Display strategy parameters in a formatted way
    
    Args:
        params: Strategy parameters dictionary
    """
    st.subheader("Strategy Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Midprice:** {params.get('midprice', 'N/A')}")
        st.write(f"**Grid Distance:** {params.get('grid_distance', 'N/A')}")
        st.write(f"**Grid Range:** {params.get('grid_range', 'N/A')}")
    
    with col2:
        st.write(f"**Grid Levels:** {params.get('grid_levels_count', 'N/A')}")
        st.write(f"**ATR Multiplier:** {params.get('atr_multiplier', 'N/A')}")
        st.write(f"**TP/SL Ratio:** {params.get('tp_sl_ratio', 'N/A')}")
