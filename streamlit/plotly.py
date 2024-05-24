import streamlit as st
import numpy as np
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Function to round numbers to the nearest 25
def round_25(number):
    return 25 * round(number / 25)

# Streamlit App Title
st.title('BinanceP2P USDT-MMK market')

# Define the UTC offset for your timezone (e.g., UTC-4 for New York)
utc_offset = timedelta(hours=+6.5)
local_timezone = timezone(utc_offset)

# Get the current time in the specified timezone
now = datetime.now(local_timezone)
current_time = now.strftime("%d-%b-%Y %H:%M:%S %Z%z")

# Display the current time with timezone information
st.write(f"Last update: {current_time}")

# Binance API link and headers
link = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}

# Function to fetch data from Binance API
def fetch_data(payload):
    with requests.Session() as s:
        s.headers.update(headers)
        res = s.post(link, json=payload)
        return res.json()['data']

# Payloads for different API requests
payload_buy_1 = {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"}
payload_sell_1 = {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "SELL"}
payload_buy_2 = {"proMerchantAds": False, "page": 2, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"}
payload_sell_2 = {"proMerchantAds": False, "page": 2, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "SELL"}

# Fetch and combine data
data = fetch_data(payload_buy_1)
data.extend(fetch_data(payload_sell_1))
data.extend(fetch_data(payload_buy_2))
data.extend(fetch_data(payload_sell_2))

# Process data into a DataFrame
result = [dict(pair for d1 in d.values() for pair in d1.items()) for d in data]
x = list(map(lambda x: x["price"], result))
y = list(map(lambda y: y["tradableQuantity"], result))
z = list(map(lambda z: z["tradeType"], result))
combineddata = [{'price': price, 'limit': limit, 'buysell': buysell} for price, limit, buysell in zip(x, y, z)]
df = pd.DataFrame(data=combineddata)

# Convert columns to appropriate types
df.price = df.price.astype("float")
df.limit = df.limit.astype("float")
df.buysell = df.buysell.astype("str")
buy = df.loc[df.buysell == 'BUY']
sell = df.loc[df.buysell == 'SELL']

# Filter outliers (optional step, adjust as needed)
price_lower_quantile = df.price.quantile(0.05)
price_upper_quantile = df.price.quantile(0.95)
df = df[(df.price >= price_lower_quantile) & (df.price <= price_upper_quantile)]

buy = df.loc[df.buysell == 'BUY']
sell = df.loc[df.buysell == 'SELL']

# Find the highest buy price and lowest sell price
highest_buy = buy.loc[buy.price.idxmax()]
lowest_sell = sell.loc[sell.price.idxmin()]

# Rounding for x-axis ticks
min_round = round_25(min(df.price))
max_round = round_25(max(df.price))

# Plotting with Plotly
color_discrete_map = {'BUY': 'green', 'SELL': 'red'}
fig = px.scatter(df, x='price', y='limit', color='buysell', log_y=True,
                 labels={'price': 'Price of USDT (MMK)', 'limit': 'Order Amount (USDT)'},
                 title=f"Last update: {current_time}",
                 color_discrete_map=color_discrete_map,
                 hover_data=['price', 'limit', 'buysell'])

# Add annotations for highest buy and lowest sell
fig.add_trace(go.Scatter(
    x=[highest_buy['price']],
    y=[highest_buy['limit']],
    mode='text',
    text=[highest_buy['price']],
    textposition='top right',
    showlegend=False,
    marker=dict(color='green')
))

fig.add_trace(go.Scatter(
    x=[lowest_sell['price']],
    y=[lowest_sell['limit']],
    mode='text',
    text=[lowest_sell['price']],
    textposition='top right',
    showlegend=False,
    marker=dict(color='red')
))

fig.update_layout(
    xaxis=dict(tickmode='linear', dtick=25, range=[min_round, max_round]),
    yaxis=dict(tickvals=[100, 250, 500, 1000, 2000, 5000, 10000, 50000, 100000, 200000, 500000, 1000000],
               ticktext=[100, 250, 500, "1k", "2k", "5k", "10k", "50k", "100k", "200k", "500k", "1M"])
)

# Display the plot in Streamlit
st.plotly_chart(fig)
