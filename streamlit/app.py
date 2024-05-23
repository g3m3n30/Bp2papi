import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import sqlite3
import threading
import time

# Function to set up the database
def setup_database():
    conn = sqlite3.connect('binance_p2p.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS p2p_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            price REAL,
            trade_limit REAL,
            buysell TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to fetch data from Binance API
def fetch_data(payload):
    link = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    with requests.Session() as s:
        s.headers.update(headers)
        res = s.post(link, json=payload)
        return res.json()['data']

# Function to insert data into the database
def insert_data(data):
    conn = sqlite3.connect('binance_p2p.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in data:
        c.execute('''
            INSERT INTO p2p_data (timestamp, price, trade_limit, buysell)
            VALUES (?, ?, ?, ?)
        ''', (now, item['price'], item['trade_limit'], item['buysell']))
    conn.commit()
    conn.close()

# Function to fetch and process data
def fetch_and_store_data():
    payload_buy_1 = {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"}
    payload_sell_1 = {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "SELL"}
    payload_buy_2 = {"proMerchantAds": False, "page": 2, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"}
    payload_sell_2 = {"proMerchantAds": False, "page": 2, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "SELL"}

    data = fetch_data(payload_buy_1)
    data.extend(fetch_data(payload_sell_1))
    data.extend(fetch_data(payload_buy_2))
    data.extend(fetch_data(payload_sell_2))

    result = [dict(pair for d1 in d.values() for pair in d1.items()) for d in data]
    x = list(map(lambda x: x["price"], result))
    y = list(map(lambda y: y["tradableQuantity"], result))
    z = list(map(lambda z: z["tradeType"], result))
    combineddata = [{'price': price, 'trade_limit': limit, 'buysell': buysell} for price, limit, buysell in zip(x, y, z)]
    
    insert_data(combineddata)

# Function to fetch and store data periodically
def periodic_fetch_and_store(interval):
    while True:
        fetch_and_store_data()
        time.sleep(interval)

# Set up the database (this will only create the table if it doesn't exist)
setup_database()

# Start a background thread to fetch and store data every hour (3600 seconds)
threading.Thread(target=periodic_fetch_and_store, args=(3600,), daemon=True).start()

# Main Streamlit app
st.title('BinanceP2P USDT-MMK market')

# Display the current time
now = datetime.now()
current_time = now.strftime("%d-%b-%Y %H:%M:%S")
st.write(f"Last update: {current_time}")

# Querying historical data from the database
def fetch_historical_data():
    conn = sqlite3.connect('binance_p2p.db')
    df = pd.read_sql_query("SELECT * FROM p2p_data", conn)
    conn.close()
    return df

# Fetch historical data
historical_df = fetch_historical_data()

# Convert timestamp to datetime
historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'])

# Plot historical data
fig, ax = plt.subplots()
sns.lineplot(x='timestamp', y='price', hue='buysell', data=historical_df, ax=ax)
ax.set_title("Historical P2P Prices")
ax.set_xlabel("Timestamp")
ax.set_ylabel("Price (MMK)")
plt.xticks(rotation=45)
st.pyplot(fig)
