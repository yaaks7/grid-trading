# Data Directory

This directory contains all data-related files for the Grid Trading Strategy project.

## Structure

```
data/
├── results/        # Backtest results, performance reports, trade logs
├── cache/          # Cached market data to avoid repeated API calls
└── README.md       # This file
```

## File Types

### `/results/`
- `*.csv` - Backtest results and performance metrics
- `*.json` - Strategy parameters and configuration snapshots
- `*.html` - Generated charts and reports

### `/cache/`
- `*.pkl` - Cached market data from yfinance
- `*.json` - Metadata about cached data

## Usage

All data files are automatically managed by the application:
- Results are saved when running backtests
- Cache files are created to speed up repeated data requests
- Clean old files periodically to save disk space

## Gitignore

Data files are excluded from version control to keep the repository clean.
