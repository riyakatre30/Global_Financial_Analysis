import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Global Trading Dashboard",
                   layout="wide",
                   page_icon="📊")

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

st.sidebar.title("🌍 Market Selector")

country = st.sidebar.selectbox(
    "Select Country",
    df["Country"].unique()
)

filtered_country = df[df["Country"] == country]

company = st.sidebar.selectbox(
    "Select Company",
    filtered_country["Company"].unique()
)

filtered_df = filtered_country[filtered_country["Company"] == company]

# -------------------- HEADER --------------------

st.title(f"📈 {company} Stock Dashboard")
st.markdown(f"#### Country: {country}")

# -------------------- KPI CARDS --------------------

col1, col2, col3, col4 = st.columns(4)

latest_price = filtered_df["Close"].iloc[-1]
high_price = filtered_df["High"].max()
low_price = filtered_df["Low"].min()
avg_price = filtered_df["Close"].mean()

col1.metric("💰 Latest Price", f"{latest_price:.2f}")
col2.metric("🔼 Highest", f"{high_price:.2f}")
col3.metric("🔽 Lowest", f"{low_price:.2f}")
col4.metric("📊 Average", f"{avg_price:.2f}")

# -------------------- MAIN DASHBOARD LAYOUT --------------------

left_col, right_col = st.columns([2, 1])

# ---------- PRICE CHART (Google Style) ----------
with left_col:

    chart_type = st.radio("Chart Type", ["Line Chart", "Candlestick"], horizontal=True)

    if chart_type == "Line Chart":
        fig = px.line(
            filtered_df,
            x="Date",
            y="Close",
            template="plotly_dark"
        )
    else:
        fig = go.Figure(data=[go.Candlestick(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"]
        )])

        fig.update_layout(template="plotly_dark")

    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ---------- PIE CHART SECTION ----------
with right_col:

    st.subheader("📌 Price Distribution")

    pie_data = pd.DataFrame({
        "Type": ["High Avg", "Low Avg"],
        "Value": [
            filtered_df["High"].mean(),
            filtered_df["Low"].mean()
        ]
    })

    fig_pie = px.pie(
        pie_data,
        names="Type",
        values="Value",
        template="plotly_dark"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📅 Date Range")

    st.write("Start:", filtered_df["Date"].min().date())
    st.write("End:", filtered_df["Date"].max().date())
