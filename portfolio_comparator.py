import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

# ==========================================
# 1. DYNAMIC INPUT & SYSTEM SYNC
# ==========================================
print("\n" + "—"*40)
print(" ⚡ MARKET INTELLIGENCE TERMINAL V2.0")
print("—"*40)
user_input = input("Enter Tickers (e.g. NVDA, AAPL, BTC-USD, ETH-GBP): ")

tickers = [t.strip().upper() for t in user_input.split(',')]

try:
    df = yf.download(tickers, period="1y", interval="1d", progress=False)['Close']
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(1)
except Exception as e:
    print(f"Connection Error: {e}")
    sys.exit()

# ==========================================
# 2. QUANTITATIVE ANALYSIS
# ==========================================
results = []
for ticker in tickers:
    if ticker not in df.columns: continue
    prices = df[ticker].dropna()
    if len(prices) < 2: continue

    ret = ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100
    log_rets = np.log(prices / prices.shift(1)).dropna()
    vol = log_rets.std() * np.sqrt(252) * 100
    score = ret / vol if vol != 0 else 0

    results.append({'Ticker': ticker, 'Return': ret, 'Risk': vol, 'Efficiency': score})

report_df = pd.DataFrame(results).sort_values(by='Efficiency', ascending=False)

# ==========================================
# 3. UI/UX: THE MODERN "SLATE" DASHBOARD
# ==========================================
fig = make_subplots(
    rows=2, cols=1,
    vertical_spacing=0.08,
    row_heights=[0.3, 0.7],
    specs=[[{"type": "table"}], [{"type": "scatter"}]],
    subplot_titles=("", "") # Titles are moved into annotations for better design
)

# A. Modern Glass-Style Table
fig.add_trace(
    go.Table(
        header=dict(
            values=["ASSET", "RETURN (%)", "RISK (%)", "EFFICIENCY SCORE"],
            fill_color='#161b22', # Dark Slate
            align='center',
            font=dict(color='#58a6ff', size=14, family="Arial Black"),
            height=40,
            line_color='#30363d'
        ),
        cells=dict(
            values=[report_df.Ticker, 
                    report_df.Return.round(2), 
                    report_df.Risk.round(2), 
                    report_df.Efficiency.round(2)],
            fill_color='#0d1117', # Deep Slate
            align='center',
            font=dict(color='#c9d1d9', size=13),
            height=35,
            line_color='#30363d'
        )
    ), row=1, col=1
)

# B. Neon Gradient Scatter Plot
fig.add_trace(
    go.Scatter(
        x=report_df['Risk'], y=report_df['Return'],
        mode='markers+text',
        text=report_df['Ticker'],
        textposition="top center",
        marker=dict(
            size=24,
            color=report_df['Efficiency'],
            colorscale='Turbo', # Brighter, more modern scale
            showscale=True,
            colorbar=dict(title="Efficiency", x=1.02, thickness=15),
            line=dict(width=2, color='rgba(255, 255, 255, 0.5)') # Soft white glow
        ),
        hovertemplate="<b>%{text}</b><br>Risk: %{x}%<br>Return: %{y}%<extra></extra>"
    ), row=2, col=1
)

# C. Modern Quadrant Lines
avg_risk, avg_ret = report_df['Risk'].mean(), report_df['Return'].mean()
fig.add_shape(type="line", x0=avg_risk, x1=avg_risk, y0=report_df['Return'].min()*0.8, y1=report_df['Return'].max()*1.2,
              line=dict(color="rgba(255,255,255,0.2)", width=1, dash="dot"), row=2, col=1)
fig.add_shape(type="line", x0=report_df['Risk'].min()*0.8, x1=report_df['Risk'].max()*1.2, y0=avg_ret, y1=avg_ret,
              line=dict(color="rgba(255,255,255,0.2)", width=1, dash="dot"), row=2, col=1)

# D. The "Senior" Layout Polish
fig.update_layout(
    title={
        'text': "<b>MARKET INTELLIGENCE</b> <span style='color:#58a6ff'>STRATEGIC MAPPING</span>",
        'y': 0.96, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
        'font': {'size': 28, 'color': '#FFFFFF', 'family': 'Arial'}
    },
    template='plotly_dark',
    paper_bgcolor='#0d1117', # The modern "GitHub Dark" slate
    plot_bgcolor='#0d1117',
    height=950,
    margin=dict(t=120, b=80, l=100, r=100),
    font=dict(family="Inter, sans-serif")
)

fig.update_xaxes(title_text="ANNUALISED RISK (%)", gridcolor='#21262d', zeroline=False, row=2, col=1)
fig.update_yaxes(title_text="ANNUALISED RETURN (%)", gridcolor='#21262d', zeroline=False, row=2, col=1)

print("\nUI Overhaul Complete. Launching Modern Dashboard...")
fig.show()