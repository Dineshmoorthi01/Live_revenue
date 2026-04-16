import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import sqlite3
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Live Revenue Pulse",
    layout="wide",
    page_icon="📊"
)

# -------------------------------------------------
# AUTO REFRESH EVERY 30 SECONDS
# -------------------------------------------------

st_autorefresh(interval=30 * 1000, key="datarefresh")

# -------------------------------------------------
# DATABASE
# -------------------------------------------------

conn = sqlite3.connect("sales.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
id INTEGER PRIMARY KEY AUTOINCREMENT,
time TEXT,
product TEXT,
price REAL,
city TEXT,
weather TEXT
)
""")

conn.commit()

# -------------------------------------------------
# FAKE DATA GENERATOR
# -------------------------------------------------

products = [
    "Laptop",
    "Mobile",
    "Headphones",
    "Keyboard",
    "Monitor",
    "Mouse",
    "Tablet",
    "Smart Watch"
]

cities = [
    "Chennai",
    "Bangalore",
    "Hyderabad",
    "Mumbai",
    "Delhi",
    "Pune"
]

prices = [25000, 35000, 1500, 2000, 12000, 800, 22000, 7000]


# -------------------------------------------------
# WEATHER API
# -------------------------------------------------

def get_weather(city):

    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=3)
        data = response.json()

        condition = data['current_condition'][0]['weatherDesc'][0]['value']

        if "rain" in condition.lower():
            return "Rain 🌧️"

        if "cloud" in condition.lower():
            return "Cloudy ☁️"

        if "sun" in condition.lower():
            return "Heat ☀️"

        return "Normal 🌤️"

    except:
        return "Unknown"


# -------------------------------------------------
# GENERATE FAKE SALE
# -------------------------------------------------

def generate_sale():

    product = random.choice(products)
    price = random.choice(prices)
    city = random.choice(cities)
    weather = get_weather(city)

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO sales(time,product,price,city,weather)
    VALUES(?,?,?,?,?)
    """, (time_now, product, price, city, weather))

    conn.commit()


# Generate new sale every refresh
generate_sale()

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

df = pd.read_sql("SELECT * FROM sales", conn)

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("🚀 Live Revenue Pulse Dashboard")

st.caption("Live Sales Monitoring | Weather Impact | Auto Updating")

# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------

total_revenue = df["price"].sum()
total_orders = len(df)
avg_order = df["price"].mean()

col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Total Revenue",
    f"₹{int(total_revenue):,}"
)

col2.metric(
    "📦 Orders",
    total_orders
)

col3.metric(
    "📊 Avg Order",
    f"₹{int(avg_order)}"
)

st.divider()

# -------------------------------------------------
# LIVE SALES TABLE
# -------------------------------------------------

st.subheader("🟢 Live Sales Feed")

st.dataframe(
    df.sort_values("id", ascending=False).head(10),
    use_container_width=True
)

# -------------------------------------------------
# CHARTS
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("📈 Revenue by City")

    city_chart = df.groupby("city")["price"].sum().reset_index()

    fig = px.bar(
        city_chart,
        x="city",
        y="price",
        text="price",
        color="city"
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    st.subheader("🌦️ Weather Impact")

    weather_chart = df.groupby("weather")["price"].sum().reset_index()

    fig2 = px.pie(
        weather_chart,
        names="weather",
        values="price"
    )

    st.plotly_chart(fig2, use_container_width=True)


# -------------------------------------------------
# SALES TREND
# -------------------------------------------------

st.subheader("📊 Sales Trend")

df["time"] = pd.to_datetime(df["time"])

trend = df.set_index("time").resample("1min")["price"].sum()

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=trend.index,
        y=trend.values,
        mode='lines+markers'
    )
)

st.plotly_chart(fig3, use_container_width=True)


# -------------------------------------------------
# CITY WEATHER STATUS
# -------------------------------------------------

st.subheader("🌍 City Weather Impact")

city_weather = df.groupby(["city", "weather"]).size().reset_index()

st.dataframe(city_weather, use_container_width=True)


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.caption(
    f"Last Updated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)