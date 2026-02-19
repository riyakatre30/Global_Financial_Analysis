import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Global Trading Dashboard",
                   layout="wide",
                   page_icon="📈")

# -------------------- LOAD DATA --------------------

@st.cache_data
def load_data():
    india = pd.read_csv("Global_Financial_Analysis/Stock_NS.csv")
    usa = pd.read_csv("Global_Financial_Analysis/Stock_USA.csv")
    canada = pd.read_csv("Global_Financial_Analysis/Stock_Canada.csv")
    germany = pd.read_csv("Global_Financial_Analysis/Stock_Germany.csv")
    france = pd.read_csv("Global_Financial_Analysis/Stock_France.csv")
    shanghai = pd.read_csv("Global_Financial_Analysis/Stock_Shanghai.csv")
    hongkong = pd.read_csv("Global_Financial_Analysis/Stock_HK.csv")
    london = pd.read_csv("Global_Financial_Analysis/Stock_L.csv")
    tokyo = pd.read_csv("Global_Financial_Analysis/Stock_Tokyo.csv")
    australia = pd.read_csv("Global_Financial_Analysis/Stock_Australia.csv")

    india["Country"] = "India"
    usa["Country"] = "USA"
    canada["Country"] = "Canada"
    germany["Country"] = "Germany"
    france["Country"] = "France"
    shanghai["Country"] = "Shanghai"
    hongkong["Country"] = "Hong Kong"
    london["Country"] = "London"
    tokyo["Country"] = "Tokyo"
    australia["Country"] = "Australia"

    df = pd.concat([india, usa, canada, germany, france,
                    shanghai, hongkong, london, tokyo,
                    australia], axis=0)

    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# -------------------- SIDEBAR --------------------

st.sidebar.title("🌍 Global Market Filter")

country = st.sidebar.multiselect(
    "Select Country",
    options=df["Country"].unique(),
    default=df["Country"].unique()
)

filtered_country = df[df["Country"].isin(country)]

stock = st.sidebar.multiselect(
    "Select Company (Stock)",
    options=filtered_country["Stock"].unique(),
    default=filtered_country["Stock"].unique()[:3]
)

filtered_df = filtered_country[filtered_country["Stock"].isin(stock)]

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
st.markdown("### Live Market Style Analysis")

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

fig = px.line(filtered_df,
              x="Date",
              y="Close",
              color="Stock",
              template="plotly_dark")

fig.update_layout(
    xaxis_rangeslider_visible=True,
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# -------------------- CANDLESTICK CHART --------------------

st.subheader("🕯️ Candlestick Chart")

stock_choice = st.selectbox("Select Stock for Candlestick",
                            filtered_df["Stock"].unique())

candlestick_df = filtered_df[filtered_df["Stock"] == stock_choice]

fig2 = go.Figure(data=[go.Candlestick(
    x=candlestick_df["Date"],
    open=candlestick_df["Open"],
    high=candlestick_df["High"],
    low=candlestick_df["Low"],
    close=candlestick_df["Close"]
)])

fig2.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------- VOLUME CHART --------------------

st.subheader("📊 Volume Analysis")

fig3 = px.bar(candlestick_df,
              x="Date",
              y="Volume",
              template="plotly_dark")

st.plotly_chart(fig3, use_container_width=True)
