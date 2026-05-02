import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

# ==========================================
# 1. DATA INGESTION & NORMALISATION
# ==========================================
ticker = input("Enter Asset Ticker (e.g. NVDA, BTC-USD, AAPL): ").upper()

print(f"Initialising connection for {ticker}...")

try:
    # Fetching historical daily price action
    df = yf.download(ticker, period="1y", interval="1d")
    
    # FIX: Flatten MultiIndex columns if they exist (prevents the 'Ambiguous Series' error)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
except Exception as e:
    print(f"Connection Error: {e}")
    sys.exit()

# Defensive validation gateway
if df.empty:
    print(f"\n[!] ALERT: Data validation failed for '{ticker}'.")
    print("Process terminated safely. Verify the asset symbol.")
    sys.exit()

# Quantitative Analysis: Calculating the 20-day Simple Moving Average (SMA)
df['SMA_20'] = df['Close'].rolling(window=20).mean()

# Removing initial null values for a clean output
df.dropna(inplace=True)

# ==========================================
# 2. UI/UX: HIGH-RESILIENCY ARCHITECTURE
# ==========================================

# Subplot configuration
viz = make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03, 
    row_heights=[0.7, 0.3],
    subplot_titles=(None, '<b>MARKET VOLUME</b>') 
)

# A. Visualising Price Action
viz.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'], 
    high=df['High'],
    low=df['Low'], 
    close=df['Close'],
    increasing_line_color='#26a69a', 
    decreasing_line_color='#ef5350',
    increasing_fillcolor='#26a69a',
    decreasing_fillcolor='#ef5350',
    name='Price Action'
), row=1, col=1)

# B. Visualising Technical Indicator (SMA)
viz.add_trace(go.Scatter(
    x=df.index, 
    y=df['SMA_20'], 
    line=dict(color='#f0b90b', width=2.5), 
    name='20D SMA Trend'
), row=1, col=1)

# C. Visualising Market Volume with Conditional Colouring
# The logic below now works because the columns were flattened above
bar_colours = ['#ef5350' if row['Open'] > row['Close'] else '#26a69a' for _, row in df.iterrows()]

viz.add_trace(go.Bar(
    x=df.index, 
    y=df['Volume'], 
    marker=dict(color=bar_colours),
    name='Volume'
), row=2, col=1)

# D. Master Layout Optimisation
viz.update_layout(
    title={
        'text': f'MARKET INTELLIGENCE GATEWAY: <b>{ticker}</b>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 26, 'color': '#FFFFFF'}
    },
    template='plotly_dark',
    paper_bgcolor='#101010', 
    plot_bgcolor='#101010',
    
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=12, color='gray')
    ),
    
    xaxis=dict(gridcolor='#222222', tickfont=dict(color='gray')),
    xaxis2=dict(gridcolor='#222222', tickfont=dict(color='gray')),
    yaxis=dict(showgrid=True, gridcolor='#222222', tickfont=dict(color='gray'), title='Price (USD)'),
    yaxis2=dict(showgrid=True, gridcolor='#222222', tickfont=dict(color='gray')),
    
    margin=dict(l=60, r=60, t=120, b=60),
    hovermode='x unified' 
)

# E. Interactive Range Selectors
viz.update_xaxes(
    rangeslider_visible=False,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(step="all")
        ]),
        bgcolor="#1A1A1A",
        activecolor="#f0b90b",
        font=dict(color="white", size=11),
        y=1.02,
        x=0
    ),
    row=1, col=1
)

viz.update_annotations(font_color="white", font_size=14)

print("Optimising UI... Dashboard launching in browser.")
viz.show()