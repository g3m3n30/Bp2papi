import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler

# Database functions
def init_db():
    conn = sqlite3.connect('binance_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS p2p_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        price REAL,
        limit REAL,
        buysell TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def fetch_and_store_data():
    link = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    payload = {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"}

    with requests.Session() as s:
        s.headers.update(headers)
        res = s.post(link, json=payload)
        data = res.json()['data']
    
    result = [dict(pair for d1 in d.values() for pair in d1.items()) for d in data]
    x = list(map(lambda x: x["price"], result))
    y = list(map(lambda y: y["tradableQuantity"], result))
    z = list(map(lambda z: z["tradeType"], result))
    
    combineddata = [{'price': price, 'limit': limit, 'buysell': buysell} for price, limit, buysell in zip(x, y, z)]
    
    conn = sqlite3.connect('binance_data.db')
    cursor = conn.cursor()
    for entry in combineddata:
        cursor.execute("INSERT INTO p2p_data (price, limit, buysell) VALUES (?, ?, ?)", (entry['price'], entry['limit'], entry['buysell']))
    conn.commit()
    conn.close()

def get_historical_data():
    conn = sqlite3.connect('binance_data.db')
    df = pd.read_sql_query("SELECT * FROM p2p_data", conn)
    conn.close()
    return df

# Initialize the database
init_db()

# Schedule data fetching
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_data, 'interval', minutes=5)
scheduler.start()

# Initial data fetch
fetch_and_store_data()

# Streamlit app
st.title('BinanceP2P USDT-MMK market')

# Fetch and display current data
link = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}
payload = {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"}

with requests.Session() as s:
    s.headers.update(headers)
    res = s.post(link, json=payload)
    data = res.json()['data']

result = [dict(pair for d1 in d.values() for pair in d1.items()) for d in data]
x = list(map(lambda x: x["price"], result))
y = list(map(lambda y: y["tradableQuantity"], result))
z = list(map(lambda z: z["tradeType"], result))
combineddata = [{'price': price, 'limit': limit, 'buysell': buysell} for price, limit, buysell in zip(x, y, z)]
df_current = pd.DataFrame(data=combineddata)

df_current.price = df_current.price.astype("float")
df_current.limit = df_current.limit.astype("float")
df_current.buysell = df_current.buysell.astype("str")
buy = df_current.loc[df_current.buysell == 'BUY']
sell = df_current.loc[df_current.buysell == 'SELL']

# Round numbers by 25
def round_25(number):
    return 25 * round(number / 25)

min_round = round_25(min(df_current.price))
max_round = round_25(max(df_current.price))

fig, ax = plt.subplots()

ax.set_title(f"Last update: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")
sns.ecdfplot(x="price", weights="limit", stat="count", data=sell, ax=ax)
sns.ecdfplot(x="price", weights="limit", stat="count", complementary=True, data=buy, ax=ax)
sns.scatterplot(x="price", y="limit", hue="buysell", data=df_current, ax=ax)

ax.set_xlabel("Price (MMK)")
ax.set_ylabel("Tradable Amount ($)")
ax.set_yscale('log')

ax.set_xticks(np.arange(min_round, max_round + 1, 25))
ax.set_yticks([100, 250, 500, 1000, 2000, 5000, 10000, 50000, 100000, 200000, 500000, 1000000],
              ["100", "250", "500", "1k", "2k", "5k", "10k", "50k", "100k", "200k", "500k", "1M"])

st.pyplot(fig)

# Historical data visualization
df_historical = get_historical_data()
df_historical['timestamp'] = pd.to_datetime(df_historical['timestamp'])

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=df_historical, x='timestamp', y='price', hue='buysell', ax=ax2)
ax2.set_title('Price Over Time')
ax2.set_xlabel('Timestamp')
ax2.set_ylabel('Price')

st.pyplot(fig2)
