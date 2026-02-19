import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Stock Analysis Dashboard",
                   layout="wide",
                   page_icon="📈")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "Global_Stock_Data.csv")

    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Select Stock")

country = st.sidebar.selectbox(
    "Select Country",
    sorted(df["Country"].dropna().unique())
)

country_df = df[df["Country"] == country]

company = st.sidebar.selectbox(
    "Select Company",
    sorted(country_df["Company"].dropna().unique())
)

filtered_df = country_df[country_df["Company"] == company]

start_date = st.sidebar.date_input("Start Date", filtered_df["Date"].min())
end_date = st.sidebar.date_input("End Date", filtered_df["Date"].max())

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("No data available")
    st.stop()

# ---------------- HEADER ----------------
latest_price = filtered_df["Close"].iloc[-1]
first_price = filtered_df["Close"].iloc[0]
change = latest_price - first_price
percent = (change / first_price) * 100

st.title(company)
st.caption(f"{country} Market")

if percent >= 0:
    st.markdown(f"### ₹ {latest_price:.2f}  🔼  {percent:.2f}%")
else:
    st.markdown(f"### ₹ {latest_price:.2f}  🔽  {percent:.2f}%")

# ---------------- KPI CARDS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Highest Price", f"{filtered_df['High'].max():.2f}")
col2.metric("Lowest Price", f"{filtered_df['Low'].min():.2f}")
col3.metric("Total Volume", f"{int(filtered_df['Volume'].sum())}")

# ---------------- CHART TYPE ----------------
chart_type = st.radio(
    "Chart View",
    ["Line", "Candlestick"],
    horizontal=True
)

fig = go.Figure()

if chart_type == "Line":
    fig.add_trace(go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["Close"],
        mode='lines',
        name='Close Price'
    ))
else:
    fig.add_trace(go.Candlestick(
        x=filtered_df["Date"],
        open=filtered_df["Open"],
        high=filtered_df["High"],
        low=filtered_df["Low"],
        close=filtered_df["Close"],
        name="Candlestick"
    ))

fig.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- VOLUME CHART ----------------
st.subheader("Volume Analysis")

fig_volume = px.bar(
    filtered_df,
    x="Date",
    y="Volume",
    template="plotly_dark"
)

fig_volume.update_layout(height=300)

st.plotly_chart(fig_volume, use_container_width=True)

# ---------------- SIMPLE ANALYSIS ----------------
st.subheader("Quick Insight")

if percent > 0:
    st.success("Stock is showing upward trend in selected period.")
elif percent < 0:
    st.error("Stock is showing downward trend in selected period.")
else:
    st.info("Stock price is stable in selected period.")
