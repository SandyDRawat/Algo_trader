# Trading Simulator and Strategy Backtesting Framework

This project is a comprehensive tool for traders and developers to backtest trading strategies, visualize their historical performance, and practice live trading simulation. With features for plotting buy/sell points on candlestick charts and tracking real-time positions and PnL, it bridges the gap between theoretical strategy testing and practical trading practice.

---

## Features

### 1. **Backtesting Framework**
- Evaluate the historical performance of multiple trading strategies.
- Support for popular technical indicators such as RSI, SMA, Bollinger Bands, MACD, etc.
- Includes pre-built strategies such as:
  - Bollinger Bands (BB) Strategy
  - Intraday Gap Strategy
  - MACD Crossover Strategy
  - Mean Reversion Strategy
  - RSI Strategy
  - SMA Strategy

### 2. **Interactive Candlestick Visualization**
- Visualize candlestick charts with buy/sell points marked based on strategy logic.
- Retain zoom levels, custom drawings, and annotations when navigating charts.
- Switch timeframes interactively while retaining chart states.

### 3. **Live Trading Simulation Tool**
- Simulates a real-time trading environment by advancing candles one at a time upon clicking the "Next" button.
- Allows users to create buy or sell positions based on current chart data.
- Tracks PnL throughout the simulation, helping users refine their trading decisions.

---

## Project Structure

```Plaintext
📦trading-simulator
 ┣ 📂Charts              # Chart visualization module
 ┃ ┗ 📜candle_chart.py   # Logic for plotting candlestick charts
 ┣ 📂data                # Folder for storing historical trading data
 ┃ ┗ 📜NIFTY50-Minute_data.csv
 ┣ 📂Evaluation          # Strategy performance evaluation module
 ┃ ┗ 📜strategy_performance.py
 ┣ 📂Practice            # Live trading simulation module
 ┃ ┣ 📜performance.py    # PnL tracking logic
 ┃ ┣ 📜random.py         # Randomized data handling
 ┃ ┗ 📜practice_plotter.py # Live trading simulation UI
 ┣ 📂preprocessing       # Data preprocessing module
 ┃ ┣ 📜cleaning.py       # Data cleaning logic
 ┃ ┣ 📜data_ingest.py    # Data ingestion logic
 ┃ ┣ 📜indicator.py      # Indicator calculation logic
 ┃ ┗ 📜timeframe.py      # Timeframe conversion logic
 ┣ 📂Strategy            # Trading strategies implementation
 ┃ ┣ 📜BB_strategy.py    # Bollinger Bands strategy
 ┃ ┣ 📜Intraday_gap_strategy.py # Intraday gap strategy
 ┃ ┣ 📜MACD_crossover_strategy.py # MACD crossover strategy
 ┃ ┣ 📜Mean_reversion_strategy.py # Mean reversion strategy
 ┃ ┣ 📜multi_indicator_strategy.py # Multi-indicator strategy
 ┃ ┣ 📜RSI_strategy.py   # RSI strategy
 ┃ ┗ 📜SMA_strategy.py   # Simple Moving Average strategy
 ┣ 📜.gitignore          # Git ignore file
 ┣ 📜backtest.py         # Main backtesting script
 ┣ 📜README.md           # Project documentation
 ┗ 📜requirements.txt    # Python dependencies
```
---

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/SandyDRawat/Algo_trader
    cd Algo_trader
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install required packages:**
    ```sh
    pip install -r requirements.txt
    ```

---

## Usage

### **Backtesting**
To backtest a trading strategy:
```sh
python backtest.py
```
This script:
- Loads historical data.
- Cleans and preprocesses it.
- Applies selected indicators and strategies.
- Evaluates the strategy’s performance.

### **Interactive Practice Tool**
To run the live trading simulation:
```sh
python practice_plotter.py
```
This script:
- Displays an interactive candlestick chart.
- Allows users to simulate trades based on candle-by-candle progression.
- Tracks real-time positions and PnL.

### **Other Functionalities**
- **Data Cleaning:**
  Use `cleaning.py` to preprocess and clean raw data.
- **Indicator Calculation:**
  Add technical indicators using `indicator.py`.
- **Timeframe Conversion:**
  Use `timeframe.py` to resample data to desired timeframes.

---

## Requirements

- Python 3.8 or higher
- Dash
- Plotly
- Pandas
- Numpy

Install all dependencies with:
```sh
pip install -r requirements.txt
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

Happy trading and learning!

