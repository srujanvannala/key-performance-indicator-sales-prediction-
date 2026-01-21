import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Power BI Style Sales KPI Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Dark Theme CSS
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.kpi-card {
    background-color: #1E1E1E;
    padding: 20px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.6);
}
.kpi-title {
    font-size: 14px;
    color: #B0B0B0;
}
.kpi-value {
    font-size: 32px;
    font-weight: bold;
}
.kpi-delta {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Power BI–Style Sales KPI Dashboard")

# -----------------------------
# CSV Upload
# -----------------------------
uploaded_file = st.file_uploader("📥 Upload Sales CSV File", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a sales CSV file to continue")
    st.stop()

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_csv(uploaded_file)
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

categories = st.sidebar.multiselect(
    "Select Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)

filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories))
]

# -----------------------------
# Month Comparison Logic (FIXED)
# -----------------------------
latest_month = filtered_df["Month"].max()
prev_month = str(pd.Period(latest_month) - 1)

current_df = filtered_df[filtered_df["Month"] == latest_month]
previous_df = filtered_df[filtered_df["Month"] == prev_month]

# -----------------------------
# KPI Calculations
# -----------------------------
sales_curr = current_df["Sales"].sum()
sales_prev = previous_df["Sales"].sum()

profit_curr = current_df["Profit"].sum()
profit_prev = previous_df["Profit"].sum()

orders = len(filtered_df)
avg_order_value = filtered_df["Sales"].sum() / orders if orders > 0 else 0

def mom_change(curr, prev):
    if prev == 0:
        return 0
    return ((curr - prev) / prev) * 100

sales_delta = mom_change(sales_curr, sales_prev)
profit_delta = mom_change(profit_curr, profit_prev)

# -----------------------------
# KPI Cards
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

def kpi_card(col, title, value, delta=None, currency=True):
    arrow = "🔺" if delta is not None and delta >= 0 else "🔻"
    color = "#00ff88" if delta is not None and delta >= 0 else "#ff4b4b"
    delta_html = (
        f"<div class='kpi-delta' style='color:{color}'>{arrow} {delta:.2f}%</div>"
        if delta is not None else ""
    )
    display_value = f"₹ {value:,.0f}" if currency else f"{value:,}"

    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{display_value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

kpi_card(c1, "💰 Total Sales (MoM)", sales_curr, sales_delta)
kpi_card(c2, "📈 Total Profit (MoM)", profit_curr, profit_delta)
kpi_card(c3, "🧾 Total Orders", orders, currency=False)
kpi_card(c4, "📊 Avg Order Value", avg_order_value)

st.markdown("---")

# -----------------------------
# Sales Trend (Interactive)
# -----------------------------
st.subheader("📅 Sales Trend")

trend_df = filtered_df.groupby("Order_Date")["Sales"].sum().reset_index()

fig_trend = px.line(
    trend_df,
    x="Order_Date",
    y="Sales",
    template="plotly_dark"
)

st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# Category-wise Donut Chart
# -----------------------------
st.subheader("📦 Category-wise Sales")

cat_df = filtered_df.groupby("Category")["Sales"].sum().reset_index()

fig_donut = px.pie(
    cat_df,
    values="Sales",
    names="Category",
    hole=0.5,
    template="plotly_dark"
)

st.plotly_chart(fig_donut, use_container_width=True)

# -----------------------------
# Region-wise Sales
# -----------------------------
st.subheader("🌍 Region-wise Sales")

region_df = filtered_df.groupby("Region")["Sales"].sum().reset_index()

fig_region = px.bar(
    region_df,
    x="Region",
    y="Sales",
    template="plotly_dark"
)

st.plotly_chart(fig_region, use_container_width=True)

# -----------------------------
# Data Preview
# -----------------------------
st.subheader("📋 Data Preview")
st.dataframe(filtered_df)
