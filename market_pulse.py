import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import sys

# --- Phase 1: Dynamic Data Ingestion ---
# Allows user to specify any asset (Stocks, Crypto, Forex)
ticker = input("Enter Asset Ticker (e.g., NVDA, BTC-USD, AAPL): ").upper()

print(f"Initializing connection for {ticker}...")

try:
    # Fetch 1 year of historical daily price action
    df = yf.download(ticker, period="1y", interval="1d")
except Exception as e:
    print(f"Network Error: Unable to reach data provider. {e}")
    sys.exit()

# --- Phase 2: Cybersecurity & Validation Guard ---
# Ensures the system fails gracefully if the ticker is invalid or data is missing
if df.empty:
    print(f"Validation Error: No market data found for symbol '{ticker}'.")
    print("Process terminated to prevent downstream calculation errors.")
    sys.exit()

# --- Phase 3: Quantitative Analysis ---
# Calculate 20-period Simple Moving Average (SMA) for trend identification
df['SMA_20'] = df['Close'].rolling(window=20).mean()

# Remove initial rows where SMA cannot be calculated (prevents chart gaps)
df.dropna(inplace=True)

# --- Phase 4: Dashboard Architecture ---
# Building an interactive visualization for technical analysis
chart = go.Figure()

# Plotting Price Action (Candlesticks)
chart.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'], 
    high=df['High'],
    low=df['Low'], 
    close=df['Close'],
    name='Price Action'
))

# Plotting the Technical Indicator (SMA)
chart.add_trace(go.Scatter(
    x=df.index, 
    y=df['SMA_20'], 
    line=dict(color='#00FFCC', width=1.5), # High-visibility Cyan
    name='20-Day SMA'
))

# Applying Professional UI/UX Settings
chart.update_layout(
    title=f'Technical Analysis: {ticker}',
    template='plotly_dark',
    xaxis_rangeslider_visible=False,
    yaxis_title='Price (USD)',
    paper_bgcolor='rgba(0,0,0,0)', # Transparent background for modern look
    plot_bgcolor='rgba(0,0,0,0)'
)

print("Analysis complete. Displaying dashboard...")
chart.show()