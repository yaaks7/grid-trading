# 📊 Asset Configuration Guide

This document provides detailed guidance on configuring grid trading parameters for different asset classes.

## 🎯 Parameter Selection Framework

### 1. **Price-Based Scaling**

Grid parameters should scale with the asset's price level:

```python
def calculate_grid_distance(price, volatility_factor=0.02):
    """
    Calculate appropriate grid distance based on price and volatility
    """
    return price * volatility_factor

# Examples:
# AAPL ($214): 214 * 0.015 = $3.21 ≈ $3
# BTC ($117,600): 117600 * 0.017 = $1,999 ≈ $2000
```

### 2. **Volatility Adjustment**

Use Average True Range (ATR) for volatility-based parameters:

```python
def atr_based_parameters(price_data, atr_period=14):
    atr = calculate_atr(price_data, atr_period)
    
    grid_distance = atr * 0.8      # 80% of daily ATR
    grid_range = atr * 10          # 10x ATR for full range
    stop_loss = atr * 1.5          # 1.5 ATR stop
    
    return grid_distance, grid_range, stop_loss
```

## 💰 Asset Class Configurations

### 📈 **Stocks (Large Cap)**

**Characteristics**:
- Moderate volatility (15-30%)
- Good liquidity
- Mean-reverting in ranges

**Configuration**:
```python
# Example: AAPL, MSFT, GOOGL
{
    'grid_distance': price * 0.014,  # ~1.4% of price
    'grid_range': price * 0.14,      # ~14% total range
    'atr_multiplier': 1.5,           # Conservative stops
    'tp_sl_ratio': 0.6,              # 60% take profit ratio
    'max_trades': 5                  # Moderate position count
}
```

**Recommended Assets**:
- AAPL: Stable, high volume
- MSFT: Consistent performer
- GOOGL: Tech sector exposure
- SPY: Market proxy

### 🚗 **Stocks (High Beta)**

**Characteristics**:
- Higher volatility (25-50%)
- More aggressive moves
- Sector-specific risks

**Configuration**:
```python
# Example: TSLA, NVDA, AMD
{
    'grid_distance': price * 0.025,  # ~2.5% of price
    'grid_range': price * 0.25,      # ~25% total range
    'atr_multiplier': 2.0,           # Wider stops
    'tp_sl_ratio': 0.5,              # Quick profits
    'max_trades': 3                  # Fewer positions
}
```

### 💱 **Forex Majors**

**Characteristics**:
- Lower volatility (8-15%)
- High liquidity
- Central bank influences

**Configuration**:
```python
# Example: EURUSD, GBPUSD
{
    'grid_distance': 0.005,          # 50 pips for majors
    'grid_range': 0.05,              # 500 pips range
    'atr_multiplier': 1.2,           # Tight stops
    'tp_sl_ratio': 0.8,              # Higher TP ratio
    'max_trades': 7                  # More positions
}
```

**Special Considerations**:
- EUR/USD: Most liquid, tight spreads
- GBP/USD: Higher volatility, Brexit impact
- USD/JPY: Safe haven flows, BoJ intervention

### 💎 **Cryptocurrencies**

**Characteristics**:
- Very high volatility (50-150%)
- 24/7 trading
- Sentiment-driven

**Configuration**:
```python
# Example: BTC-USD, ETH-USD
{
    'grid_distance': price * 0.017,  # ~1.7% for BTC
    'grid_range': price * 0.17,      # ~17% total range
    'atr_multiplier': 2.5,           # Wide stops needed
    'tp_sl_ratio': 0.4,              # Quick profit taking
    'max_trades': 3                  # Limit exposure
}
```

**Risk Warnings**:
- High volatility can cause rapid losses
- Weekend gaps common
- Regulatory risks

### 🥇 **Commodities**

**Characteristics**:
- Supply/demand driven
- Seasonal patterns
- Geopolitical sensitivity

**Configuration**:
```python
# Gold (GC=F)
{
    'grid_distance': 50,             # $50 per oz
    'grid_range': 500,               # $500 range
    'atr_multiplier': 1.8,
    'tp_sl_ratio': 0.6,
    'max_trades': 4
}

# Oil (CL=F)
{
    'grid_distance': 2.0,            # $2 per barrel
    'grid_range': 20,                # $20 range
    'atr_multiplier': 2.0,
    'tp_sl_ratio': 0.5,
    'max_trades': 4
}
```

## 🔧 Dynamic Parameter Adjustment

### Volatility Regime Detection

```python
def adjust_for_volatility_regime(base_params, current_vol, historical_vol):
    """
    Adjust parameters based on current vs historical volatility
    """
    vol_ratio = current_vol / historical_vol
    
    if vol_ratio > 1.5:  # High volatility regime
        return {
            'grid_distance': base_params['grid_distance'] * 1.3,
            'grid_range': base_params['grid_range'] * 1.2,
            'atr_multiplier': base_params['atr_multiplier'] * 1.2,
            'max_trades': max(2, base_params['max_trades'] - 1)
        }
    elif vol_ratio < 0.7:  # Low volatility regime
        return {
            'grid_distance': base_params['grid_distance'] * 0.8,
            'grid_range': base_params['grid_range'] * 0.9,
            'atr_multiplier': base_params['atr_multiplier'] * 0.9,
            'max_trades': base_params['max_trades'] + 1
        }
    else:
        return base_params
```

### Market Hours Adjustment

```python
def adjust_for_market_hours(params, asset_type):
    """
    Adjust parameters based on market hours and liquidity
    """
    if asset_type == "forex":
        # Tighter parameters during London/NY overlap
        if is_major_session_overlap():
            params['grid_distance'] *= 0.8
            params['max_trades'] += 1
    
    elif asset_type == "stocks":
        # Avoid first/last hour of trading
        if is_market_open_close():
            params['max_trades'] = max(1, params['max_trades'] - 2)
    
    return params
```

## 📊 Parameter Validation

### Backtesting Validation

```python
def validate_parameters(asset_data, params):
    """
    Validate parameter effectiveness through backtesting
    """
    results = backtest(asset_data, params)
    
    # Check minimum requirements
    checks = {
        'min_trades': results['total_trades'] >= 10,
        'min_winrate': results['win_rate'] >= 0.45,
        'max_drawdown': results['max_drawdown'] <= 0.15,
        'min_sharpe': results['sharpe_ratio'] >= 0.8
    }
    
    if all(checks.values()):
        return "VALID"
    else:
        return f"FAILED: {[k for k, v in checks.items() if not v]}"
```

### Real-time Monitoring

```python
def monitor_parameter_performance(live_results, benchmark_results):
    """
    Monitor if parameters need adjustment
    """
    performance_drift = {
        'return_drift': live_results['return'] - benchmark_results['return'],
        'sharpe_drift': live_results['sharpe'] - benchmark_results['sharpe'],
        'drawdown_increase': live_results['max_dd'] - benchmark_results['max_dd']
    }
    
    # Trigger re-optimization if significant drift
    if any(abs(drift) > 0.1 for drift in performance_drift.values()):
        return "REOPTIMIZE_NEEDED"
    else:
        return "PARAMETERS_OK"
```

## ⚠️ Risk Considerations by Asset

### Position Sizing by Asset Class

```python
RISK_MULTIPLIERS = {
    'large_cap_stocks': 1.0,      # Base risk
    'small_cap_stocks': 0.7,      # Reduce due to higher volatility
    'forex_majors': 1.2,          # Increase due to lower volatility
    'forex_minors': 0.8,          # Reduce due to wider spreads
    'crypto': 0.3,                # Significantly reduce due to extreme volatility
    'commodities': 0.8,           # Reduce due to gap risk
    'etfs': 1.1                   # Slightly increase due to diversification
}

def calculate_position_size(account_value, asset_class, base_risk=0.01):
    risk_multiplier = RISK_MULTIPLIERS.get(asset_class, 1.0)
    adjusted_risk = base_risk * risk_multiplier
    return account_value * adjusted_risk
```

### Correlation Adjustments

```python
def adjust_for_correlation(positions, new_asset, correlation_matrix):
    """
    Adjust position size based on existing portfolio correlations
    """
    existing_assets = [pos['asset'] for pos in positions]
    
    if not existing_assets:
        return 1.0  # No adjustment needed
    
    # Calculate average correlation with existing positions
    avg_correlation = np.mean([
        correlation_matrix[new_asset][existing] 
        for existing in existing_assets
    ])
    
    # Reduce position size for highly correlated assets
    if avg_correlation > 0.7:
        return 0.5  # 50% reduction
    elif avg_correlation > 0.4:
        return 0.7  # 30% reduction
    else:
        return 1.0  # No reduction
```

---

*This guide is part of the Grid Trading Strategy documentation.*
