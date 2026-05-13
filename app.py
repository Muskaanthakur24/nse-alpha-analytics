import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="NSE Alpha Analytics", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    h1 { color: #60A5FA; font-size: 2.8rem; }
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📊 NSE Alpha Analytics")
st.markdown("**Professional Dashboard for Indian Stock Market**")
st.caption(f"Updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# Sidebar
st.sidebar.header("🔍 Dashboard Controls")
ticker = st.sidebar.text_input("Enter NSE Stock Symbol", "HDFCBANK").upper()
period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

symbol = ticker + ".NS"

@st.cache_data(ttl=60)
def fetch_data(symbol, period):
    try:
        data = yf.download(symbol, period=period, progress=False, auto_adjust=True, threads=False)
        info = yf.Ticker(symbol).info
        return data, info
    except:
        return pd.DataFrame(), {}

data, info = fetch_data(symbol, period)

if data.empty or len(data) < 5:
    st.error(f"❌ Could not load data for **{symbol}**")
    st.info("Try: HDFCBANK, TCS, INFY, ICICIBANK, SBIN")
    st.stop()

# Safe price extraction
close_series = data['Close']

# Force scalar values
price = float(close_series.iloc[-1].item() if hasattr(close_series.iloc[-1], 'item') else close_series.iloc[-1])
prev_price = float(close_series.iloc[-2].item() if hasattr(close_series.iloc[-2], 'item') else close_series.iloc[-2])

# Calculations
data['SMA_20'] = close_series.rolling(window=20).mean()

delta = close_series.diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))
# ================== KPI CARDS - FINAL SAFE VERSION ==================
col1, col2, col3, col4 = st.columns(4)

with col1:
    price = float(close_series.iloc[-1].item() if hasattr(close_series.iloc[-1], 'item') else close_series.iloc[-1])
    prev_price = float(close_series.iloc[-2].item() if hasattr(close_series.iloc[-2], 'item') else close_series.iloc[-2])
    change = (price - prev_price) / prev_price * 100
    st.metric("Current Price", f"₹{price:.2f}", f"{change:+.2f}%")

with col2:
    volume = int(float(data['Volume'].iloc[-1].item() if hasattr(data['Volume'].iloc[-1], 'item') else data['Volume'].iloc[-1]))
    st.metric("Volume", f"{volume:,}")

with col3:
    high = info.get('fiftyTwoWeekHigh', 0)
    st.metric("52W High", f"₹{float(high):.2f}" if high else "N/A")

with col4:
    mc = info.get('marketCap', 0)
    st.metric("Market Cap", f"₹{mc/1e7:.1f} Cr" if mc > 0 else "N/A")
# Charts
tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "📊 Technical Indicators", "📋 Fundamentals"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                 low=data['Low'], close=data['Close'], name="OHLC"))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], name="SMA 20", line=dict(color='orange')))
    fig.update_layout(title=f"{ticker} - Price Chart", height=650, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI"))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(title="RSI Indicator", height=400, template="plotly_dark")
    st.plotly_chart(fig_rsi, use_container_width=True)

with tab3:
    st.subheader("Company Fundamentals")
    st.write(f"**Company:** {info.get('longName', 'N/A')}")
    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
    st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
    st.write(f"**EPS:** {info.get('trailingEps', 'N/A')}")

st.success(f"✅ Successfully loaded {ticker}")