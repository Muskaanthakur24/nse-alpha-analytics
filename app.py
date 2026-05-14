import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="NSE Alpha Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    h1 { color: #60A5FA; font-size: 2.8rem; font-weight: 700; }
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📊 NSE Alpha Analytics")
st.markdown("**AI-Powered Professional Market Intelligence**")
st.caption(f"Live NSE • {datetime.now().strftime('%d %b %Y, %I:%M %p')}")