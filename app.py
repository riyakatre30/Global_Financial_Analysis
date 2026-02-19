import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Stock Dashboard",
                   layout="wide",
                   page_icon="📈")

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "Global_Stock_Data.csv")
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ---------------- SIDEBAR FILTER ----------------

st.sidebar.title("🔎 Select Market")

country = st.sidebar.selectbox("Country", df["Country"].unique())
filtered_country = df[df["Country"] == country]

company = st.sidebar.selectbox("Company", filtered_country["Company"].unique())
filtered_df = filtered_country[filtered_country["Company"] == company]

# Date Filter
min_date = filtered_df["Date"].min()
max_date = filtered_df["Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date]
)

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("No data available.")
    st.stop()

# ---------------- HEADER ----------------

latest_price = filtered_df["Close"].iloc[-1]
change = ((filtered_df["Close"].iloc[-1] -
           filtered_df["Close"].iloc[0]) /
           filtered_df["Close"].iloc[0]) * 100

st.title(company)
st.subheader(f"{country} Market")

st.metric("Current Price", f"{latest_price:.2f}",
          f"{change:.2f}%")

# ---------------- TABS ----------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "📈 Chart", "🏆 Compare", "📉 Analysis"]
)

# ====================================================
# OVERVIEW TAB
# ====================================================

with tab1:

    col1, col2, col3 = st.columns(3)

    col1.metric("High", f"{filtered_df['High'].max():.2f}")
    col2.metric("Low", f"{filtered_df['Low'].min():.2f}")
    col3.metric("Average", f"{filtered_df['Close'].mean():.2f}")

# ====================================================
# CHART TAB
# ====================================================

with tab2:

    chart_type = st.radio("Select Chart Type",
                          ["Line", "Bar", "Candlestick"],
                          horizontal=True)

    if chart_type == "Line":
        fig = px.line(filtered_df,
                      x="Date",
                      y="Close",
                      template="plotly_dark")

    elif chart_type == "Bar":
        fig = px.bar(filtered_df,
                     x="Date",
                     y="Close",
                     template="plotly_dark")

    else:
        fig = go.Figure(data=[go.Candlestick(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"]
        )])
        fig.update_layout(template="plotly_dark")

    fig.update_layout(height=500, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# ====================================================
# COMPARE TAB
# ====================================================

with tab3:

    compare_companies = st.multiselect(
        "Compare With",
        filtered_country["Company"].unique()
    )

    compare_df = filtered_country[
        filtered_country["Company"].isin(compare_companies)
    ]

    if not compare_df.empty:

        fig = px.line(compare_df,
                      x="Date",
                      y="Close",
                      color="Company",
                      template="plotly_dark")

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Top Performer
    st.subheader("Top Performer")

    perf = (
        filtered_country.groupby("Company")["Close"]
        .agg(["first", "last"])
    )

    perf["% Change"] = ((perf["last"] - perf["first"])
                        / perf["first"]) * 100

    top_company = perf["% Change"].idxmax()
    top_value = perf["% Change"].max()

    st.success(f"🏆 {top_company} is leading with {top_value:.2f}% growth")

# ====================================================
# ANALYSIS TAB
# ====================================================

with tab4:

    st.subheader("Price Insights")

    max_price = filtered_df["High"].max()
    min_price = filtered_df["Low"].min()

    st.write(f"🔼 Highest Recorded Price: {max_price:.2f}")
    st.write(f"🔽 Lowest Recorded Price: {min_price:.2f}")

    volatility = filtered_df["Close"].std()
    st.write(f"📊 Volatility (Std Dev): {volatility:.2f}")
