import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Global Trading Dashboard",
                   layout="wide",
                   page_icon="📈")

# -------------------- LOAD DATA --------------------

@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "Global_Stock_Data.csv")

    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# -------------------- SIDEBAR --------------------

st.sidebar.title("🌍 Market Filters")

country = st.sidebar.multiselect(
    "Select Country",
    options=df["Country"].unique(),
    default=df["Country"].unique()
)

filtered_country = df[df["Country"].isin(country)]

stock = st.sidebar.multiselect(
    "Select Company",
    options=filtered_country["Company"].unique(),
    default=filtered_country["Company"].unique()[:3]
)

filtered_df = filtered_country[filtered_country["Company"].isin(stock)]

start_date = st.sidebar.date_input(
    "Start Date",
    value=filtered_df["Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=filtered_df["Date"].max()
)

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

# -------------------- TITLE --------------------

st.title("📊 Global Stock Trading Dashboard")
st.markdown("#### Professional Market Analysis Platform")

# -------------------- KPIs --------------------

col1, col2, col3, col4 = st.columns(4)

latest_price = filtered_df["Close"].iloc[-1]
high_price = filtered_df["High"].max()
low_price = filtered_df["Low"].min()
change = ((filtered_df["Close"].iloc[-1] -
           filtered_df["Close"].iloc[0]) /
           filtered_df["Close"].iloc[0]) * 100

col1.metric("Latest Price", f"{latest_price:.2f}")
col2.metric("Highest Price", f"{high_price:.2f}")
col3.metric("Lowest Price", f"{low_price:.2f}")
col4.metric("Change %", f"{change:.2f}%")

# -------------------- MULTI LINE CHART --------------------

st.subheader("📈 Stock Price Comparison")

fig = px.line(
    filtered_df,
    x="Date",
    y="Close",
    color="Stock",
    template="plotly_dark"
)

fig.update_layout(
    xaxis_rangeslider_visible=True,
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# -------------------- MOVING AVERAGE --------------------

st.subheader("📉 Moving Average")

ma_stock = st.selectbox("Select Stock for MA", filtered_df["Stock"].unique())

ma_df = filtered_df[filtered_df["Stock"] == ma_stock].copy()

ma_df["MA50"] = ma_df["Close"].rolling(50).mean()
ma_df["MA200"] = ma_df["Close"].rolling(200).mean()

fig_ma = go.Figure()

fig_ma.add_trace(go.Scatter(
    x=ma_df["Date"], y=ma_df["Close"],
    mode='lines', name='Close Price'
))

fig_ma.add_trace(go.Scatter(
    x=ma_df["Date"], y=ma_df["MA50"],
    mode='lines', name='MA50'
))

fig_ma.add_trace(go.Scatter(
    x=ma_df["Date"], y=ma_df["MA200"],
    mode='lines', name='MA200'
))

fig_ma.update_layout(template="plotly_dark", height=500)

st.plotly_chart(fig_ma, use_container_width=True)

# -------------------- CANDLESTICK --------------------

st.subheader("🕯️ Candlestick Chart")

fig_candle = go.Figure(data=[go.Candlestick(
    x=ma_df["Date"],
    open=ma_df["Open"],
    high=ma_df["High"],
    low=ma_df["Low"],
    close=ma_df["Close"]
)])

fig_candle.update_layout(template="plotly_dark", height=500)

st.plotly_chart(fig_candle, use_container_width=True)

# -------------------- VOLUME --------------------

st.subheader("📊 Volume Analysis")

fig_volume = px.bar(
    ma_df,
    x="Date",
    y="Volume",
    template="plotly_dark"
)

st.plotly_chart(fig_volume, use_container_width=True)
