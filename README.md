# 📈 Grid Trading Strategy Backtester

> A modular grid trading backtesting system with interactive Streamlit interface.

## 🎯 Overview

This project implements a **grid trading strategy** with a modular architecture. The system supports multiple asset classes and provides both CLI and web interfaces for comprehensive backtesting and analysis.

### ✨ Key Features

- 🌐 **Interactive Interface**: Streamlit web application
- 📊 **Multi-Asset Support**: 48 assets across 6 classes (Tech, Finance, ETFs, Crypto, Forex, Commodities)
- ⚡ **Performance Optimized**: Smart grid generation with automatic level limiting
- 📈 **Advanced Analytics**: Comprehensive performance metrics and visualizations
- 🛡️ **Risk Management**: ATR-based stop losses and position sizing

### 🎯 **Asset Portfolio Coverage**
- **🏢 Tech Stocks**: 10 assets (AAPL, TSLA, META, NVDA, etc.)
- **🏦 Finance**: 11 assets (JPM, V, MA, PYPL, etc.)
- **📈 ETFs**: 7 assets (SPY, QQQ, XLK, XLF, etc.)
- **₿ Crypto**: 6 assets (BTC, ETH, SOL, ADA, etc.)
- **💱 Forex**: 7 pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- **🥇 Commodities**: 7 assets (Gold, Silver, Oil, Gas, etc.)

## 📱 Interface Preview

<div align="center">

![Grid Trading Interface](data/img/Capture%20d'écran%202025-07-26%20001055.png)

*Professional Streamlit interface with interactive charts and comprehensive analytics*

</div>

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yaaks7/grid-trading.git
cd grid-trading

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Web Interface (Recommended)

```bash
streamlit run streamlit_app/app.py
```

➡️ **Open [http://localhost:8501](http://localhost:8501)** in your browser

### 3. Command Line Interface

```bash
# Default backtest (AAPL, 2024)
python main.py

# Custom asset and dates
python main.py --asset BTC-USD --start 2024-06-01 --end 2024-12-31

# Dynamic midprice with verbose output
python main.py --asset EURUSD=X --dynamic --verbose
```

### 4. Quick Test

```bash
# Run unit tests
python -m pytest tests/ -v

# Test specific functionality
python tests/test_basic.py
```

## 💻 Usage Guide

### 🌐 Streamlit Interface (Two-Step Workflow)

The web interface follows a logical, pedagogical approach with an intuitive two-step workflow:

#### **Step 1: Data & Grid Configuration** 📊

Configure your trading setup and visualize the grid strategy before backtesting.

![Grid Configuration - EUR/USD](data/img/Capture%20d'écran%202025-07-25%20232720.png)
*EUR/USD configuration showing data loading, grid parameters, and initial setup*

1. **Select Asset**: Choose from AAPL, BTC-USD, EURUSD=X, etc.
2. **Set Date Range**: Pick your analysis period
3. **Configure Grid Parameters**:
   - **Midprice**: Center of the grid (static or dynamic MA-20)
   - **Grid Distance**: Spacing between levels
   - **Grid Range**: Total grid extent
4. **Load & Visualize**: See price chart with grid levels and signals

![Price Chart with Grid](data/img/Capture%20d'écran%202025-07-26%20001055.png)
*Interactive price chart showing Google stock with grid levels and trading signals*

#### **Step 2: Backtesting & Analysis** ⚙️

Configure your portfolio settings and risk management, then run comprehensive backtests.

![Backtesting Configuration](data/img/Capture%20d'écran%202025-07-26%20001106.png)
*Backtesting configuration panel with portfolio settings and risk management parameters*

1. **Portfolio Settings**: Capital, position size, max concurrent trades
2. **Risk Management**: ATR multipliers, take profit ratios
3. **Run Backtest**: Execute full analysis
4. **Review Results**: Performance metrics, equity curve, trade details

![Backtest Results](data/img/Capture%20d'écran%202025-07-26%20001118.png)
*Complete backtest results with performance metrics, equity curve, and drawdown analysis*

### 💻 CLI Interface

```bash
python main.py [OPTIONS]

Options:
  --asset {AAPL,BTC-USD,EURUSD=X,...}  Asset to backtest (default: AAPL)
  --start YYYY-MM-DD                   Start date (default: 2024-01-01)
  --end YYYY-MM-DD                     End date (default: 2024-12-31)
  --dynamic                            Use dynamic midprice (MA-20)
  --output-dir PATH                    Results directory (default: data/results)
  --verbose, -v                        Enable detailed logging
```

### 🐍 Programmatic Usage

```python
from src.data.fetcher import DataFetcher
from src.strategy.grid_trading import GridTradingStrategy
from src.backtest.backtester import GridBacktester

# Fetch data
fetcher = DataFetcher()
data = fetcher.fetch_data("AAPL", "2024-01-01", "2024-12-31", "1d")
data_with_indicators = fetcher.add_technical_indicators(data)

# Configure strategy
strategy = GridTradingStrategy(
    midprice=200,       # Price center
    grid_distance=5,    # Distance between levels  
    grid_range=50       # Total grid range
)

# Prepare data and run backtest
prepared_data = strategy.prepare_data(data_with_indicators)
backtester = GridBacktester(cash=10000)
results = backtester.run_backtest(prepared_data, {
    'position_size': 100,
    'atr_multiplier': 1.5,
    'tp_sl_ratio': 0.5,
    'max_trades': 5,
    'grid_distance': 5
})

# Get performance metrics
metrics = backtester.get_performance_metrics()
print(f"Return: {metrics['total_return']:.2f}%")
```

## 📊 Supported Assets & Recommended Configurations

**48 assets across 6 asset classes** - All parameters optimized with July 2025 market data.

### 🏢 **Stocks - Technology**
| Symbol | Name | Midprice | Grid Distance | Grid Range | 
|--------|------|----------|---------------|------------|
| AAPL | Apple | 214 | 3.0 | 30.0 |
| MSFT | Microsoft | 514 | 8.0 | 80.0 |
| GOOGL | Google | 193 | 3.0 | 30.0 |
| NVDA | NVIDIA | 174 | 5.0 | 50.0 |
| META | Meta | 713 | 8.0 | 80.0 |
| AMZN | Amazon | 231 | 4.0 | 40.0 |
| NFLX | Netflix | 1,180 | 15.0 | 150.0 |
| TSLA | Tesla | 316 | 8.0 | 80.0 |
| CRM | Salesforce | 269 | 5.0 | 50.0 |
| ADBE | Adobe | 371 | 6.0 | 60.0 |

### 🏦 **Finance & Payments**
| Symbol | Name | Midprice | Grid Distance | Grid Range |
|--------|------|----------|---------------|------------|
| JPM | JPMorgan Chase | 299 | 4.0 | 40.0 |
| BAC | Bank of America | 48 | 1.0 | 10.0 |
| GS | Goldman Sachs | 729 | 8.0 | 80.0 |
| MS | Morgan Stanley | 143 | 3.0 | 30.0 |
| V | Visa | 357 | 5.0 | 50.0 |
| MA | Mastercard | 568 | 8.0 | 80.0 |
| PYPL | PayPal | 78 | 2.0 | 20.0 |

### 📈 **ETFs - Indices & Sectors**
| Symbol | Name | Midprice | Grid Distance | Grid Range |
|--------|------|----------|---------------|------------|
| SPY | S&P 500 ETF | 637 | 5.0 | 50.0 |
| QQQ | NASDAQ ETF | 566 | 6.0 | 60.0 |
| DIA | Dow Jones ETF | 449 | 4.0 | 40.0 |
| IWM | Russell 2000 ETF | 224 | 3.0 | 30.0 |
| XLF | Financial Sector | 53 | 1.0 | 10.0 |
| XLK | Technology Sector | 262 | 3.0 | 30.0 |
| XLE | Energy Sector | 87 | 2.0 | 20.0 |

### ₿ **Cryptocurrencies**
| Symbol | Name | Midprice | Grid Distance | Grid Range |
|--------|------|----------|---------------|------------|
| BTC-USD | Bitcoin | 117,600 | 2,000 | 20,000 |
| ETH-USD | Ethereum | 3,738 | 80 | 800 |
| SOL-USD | Solana | 186 | 5.0 | 50.0 |
| ADA-USD | Cardano | 0.83 | 0.02 | 0.20 |
| DOT-USD | Polkadot | 4.12 | 0.15 | 1.50 |
| AVAX-USD | Avalanche | 24 | 0.80 | 8.0 |

### 💱 **Forex Pairs**
| Symbol | Name | Midprice | Grid Distance | Grid Range |
|--------|------|----------|---------------|------------|
| EURUSD=X | EUR/USD | 1.174 | 0.005 | 0.050 |
| GBPUSD=X | GBP/USD | 1.344 | 0.006 | 0.060 |
| USDJPY=X | USD/JPY | 147.6 | 0.50 | 5.0 |
| USDCHF=X | USD/CHF | 0.794 | 0.003 | 0.030 |
| AUDUSD=X | AUD/USD | 0.657 | 0.003 | 0.030 |
| USDCAD=X | USD/CAD | 1.37 | 0.005 | 0.050 |
| EURGBP=X | EUR/GBP | 0.874 | 0.003 | 0.030 |

### 🥇 **Commodities & Energy**
| Symbol | Name | Midprice | Grid Distance | Grid Range |
|--------|------|----------|---------------|------------|
| GC=F | Gold Futures | 3,339 | 50 | 500 |
| SI=F | Silver Futures | 38.3 | 1.0 | 10 |
| CL=F | Crude Oil | 65.1 | 2.0 | 20 |
| SLV | Silver ETF | 34.7 | 0.8 | 8.0 |
| USO | Oil ETF | 74.9 | 2.0 | 20 |
| UNG | Natural Gas ETF | 13.8 | 0.4 | 4.0 |
| DBA | Agriculture ETF | 26.1 | 0.5 | 5.0 |

*All prices and parameters updated July 2025. See [docs/ASSET_CONFIGURATION.md](docs/ASSET_CONFIGURATION.md) for detailed parameter guides.*


## 🛠️ Technical Details

### Grid Trading Strategy
- **Concept**: Place buy/sell orders at predetermined price levels
- **Signal Generation**: Execute trades when price crosses grid levels
- **Risk Management**: ATR-based stops, position sizing, concurrent trade limits
- **Optimization**: Dynamic midprice adjustment, performance-based grid sizing
- **📚 Full Documentation**: See [docs/GRID_TRADING_GUIDE.md](docs/GRID_TRADING_GUIDE.md) for complete strategy guide

### Technology Stack
- **Python 3.8+**: Core language
- **pandas/numpy**: Data manipulation
- **yfinance**: Market data
- **pandas-ta**: Technical indicators
- **backtesting.py**: Backtesting engine
- **plotly**: Interactive charts
- **streamlit**: Web interface
- **pytest**: Testing framework


## 🧪 Testing & Validation

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific functionality
python tests/test_basic.py

# Performance validation
python main.py --asset AAPL --verbose
```

## 🔧 Configuration & Customization

### Adding New Assets

Edit `config/settings.py`:
```python
SUPPORTED_ASSETS = {
    'YOUR_SYMBOL': {
        'midprice': 100.0,
        'grid_distance': 2.0,
        'grid_range': 20.0,
        'name': 'Your Asset'
    }
}
```

### Custom Technical Indicators

Extend `src/data/fetcher.py`:
```python
def add_technical_indicators(self, data):
    df = data.copy()
    df['RSI'] = ta.rsi(df.Close, length=14)
    df['MACD'] = ta.macd(df.Close)['MACD_12_26_9']
    df['YOUR_INDICATOR'] = your_custom_function(df)
    return df
```

## 📊 Output Files

All results are saved to `data/results/` with timestamps:

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Yanis Aksas**  
- GitHub: [github.com/yaaks7](https://github.com/yaaks7)
- LinkedIn: [linkedin.com/in/yanisaks](https://linkedin.com/in/yanisaks)
- Email: yanis.aksas@gmail.com


