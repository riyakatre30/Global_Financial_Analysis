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

# -------------------- SIDEBAR FILTERS --------------------

st.sidebar.title("🌍 Market Filters")

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

# ---- DATE RANGE IN SIDEBAR ----

min_date = filtered_df["Date"].min()
max_date = filtered_df["Date"].max()

start_date = st.sidebar.date_input(
    "Start Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("No data available for selected date range.")
    st.stop()

# -------------------- HEADER --------------------

st.title(f"📊 {company} Stock Dashboard")
st.markdown(f"### {country} Market")

# -------------------- KPI CARDS --------------------

col1, col2, col3, col4 = st.columns(4)

latest_price = filtered_df["Close"].iloc[-1]
high_price = filtered_df["High"].max()
low_price = filtered_df["Low"].min()
change = ((filtered_df["Close"].iloc[-1] -
           filtered_df["Close"].iloc[0]) /
           filtered_df["Close"].iloc[0]) * 100

col1.metric("💰 Latest", f"{latest_price:.2f}")
col2.metric("🔼 High", f"{high_price:.2f}")
col3.metric("🔽 Low", f"{low_price:.2f}")
col4.metric("📈 Change %", f"{change:.2f}%")

# -------------------- MAIN DASHBOARD --------------------

left, right = st.columns([3, 1])

# ---------- IMPROVED LINE CHART ----------
with left:

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["Close"],
        mode="lines",
        line=dict(width=3),
        name="Close Price"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------- SMALL PIE CHART ----------
with right:

    st.subheader("Price Split")

    pie_data = pd.DataFrame({
        "Category": ["High Avg", "Low Avg"],
        "Value": [
            filtered_df["High"].mean(),
            filtered_df["Low"].mean()
        ]
    })

    fig_pie = px.pie(
        pie_data,
        names="Category",
        values="Value",
        hole=0.5,   # donut style (modern look)
        template="plotly_dark"
    )

    fig_pie.update_layout(height=350)

    st.plotly_chart(fig_pie, use_container_width=True)
