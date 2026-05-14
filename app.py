import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="NSE Alpha Analytics", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    h1 { color: #60A5FA; font-size: 2.8rem; font-weight: 700; }
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📊 NSE Alpha Analytics")
st.markdown("**AI-Powered Professional Market Intelligence**")
st.caption(f"Live NSE Market Data • {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# Sidebar
st.sidebar.header("🔍 Stock Selection")

popular = ["HDFCBANK", "RELIANCE", "TCS", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "LT", "AXISBANK", "KOTAKBANK"]
ticker = st.sidebar.selectbox("Select Popular Stock", popular, index=0)

custom = st.sidebar.text_input("Or Type Custom Symbol", "").strip().upper()
if custom:
    ticker = custom

period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y"], index=2)

symbol = ticker + ".NS"

@st.cache_data(ttl=60)
def fetch_data(symbol, period):
    try:
        data = yf.download(symbol, period=period, progress=False)
        info = yf.Ticker(symbol).info
        return data, info
    except:
        return pd.DataFrame(), {}

data, info = fetch_data(symbol, period)

if data.empty or len(data) < 10:
    st.error(f"❌ Could not load data for **{symbol}**")
    st.info("Try another symbol")
    st.stop()

# ====================== SAFEST POSSIBLE EXTRACTION ======================
close = data['Close']

# Convert to Python scalar safely
last_close = close.iloc[-1]
prev_close = close.iloc[-2]

price = float(last_close.item() if hasattr(last_close, 'item') else last_close)
prev_price = float(prev_close.item() if hasattr(prev_close, 'item') else prev_close)

change = (price - prev_price) / prev_price * 100

volume = int(float(data['Volume'].iloc[-1].item() if hasattr(data['Volume'].iloc[-1], 'item') else data['Volume'].iloc[-1]))

# Indicators
data['SMA_20'] = close.rolling(window=20).mean()

ema12 = close.ewm(span=12, adjust=False).mean()
ema26 = close.ewm(span=26, adjust=False).mean()
data['MACD'] = ema12 - ema26
data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
data['MACD_Hist'] = data['MACD'] - data['Signal']

delta = close.diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))

# ====================== UI ======================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Price", f"₹{price:,.2f}", f"{change:+.2f}%")
with col2:
    st.metric("Volume", f"{volume:,}")
with col3:
    st.metric("52W High", f"₹{float(info.get('fiftyTwoWeekHigh', 0)):,.2f}")
with col4:
    mc = info.get('marketCap', 0)
    st.metric("Market Cap", f"₹{mc/1e7:,.1f} Cr" if mc > 0 else "N/A")

tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "📊 Technical Indicators", "📋 Fundamentals"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                 low=data['Low'], close=data['Close'], name="OHLC"))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], name="SMA 20", line=dict(color='#FBBF24')))
    fig.update_layout(title=f"{ticker} - Price Chart", height=650, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD'], name="MACD"))
        fig_macd.add_trace(go.Scatter(x=data.index, y=data['Signal'], name="Signal"))
        fig_macd.add_trace(go.Bar(x=data.index, y=data['MACD_Hist'], name="Histogram"))
        fig_macd.update_layout(title="MACD Indicator", height=380, template="plotly_dark")
        st.plotly_chart(fig_macd, use_container_width=True)
    with c2:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI"))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(title="RSI (14)", height=380, template="plotly_dark")
        st.plotly_chart(fig_rsi, use_container_width=True)

with tab3:
    st.subheader("Company Fundamentals")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Company:** {info.get('longName', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
    with c2:
        st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
        st.write(f"**EPS:** {info.get('trailingEps', 'N/A')}")

st.success(f"✅ Loaded {ticker} successfully!")