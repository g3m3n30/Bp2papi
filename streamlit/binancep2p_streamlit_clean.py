import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Streamlit App Title
st.title('BinanceP2P USDT-MMK market')

# Current Time
now = datetime.now()
current_time = now.strftime("%d-%b-%Y %H:%M:%S")
st.write(f"Last update: {current_time}")

# Binance API link and headers
link = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}

# Function to fetch data from Binance API
def fetch_data(payload):
    try:
        with requests.Session() as s:
            s.headers.update(headers)
            res = s.post(link, json=payload)
            res.raise_for_status()
            return res.json()['data']
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

# Payloads for different API requests
payloads = [
    {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"},
    {"proMerchantAds": False, "page": 1, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "SELL"},
    {"proMerchantAds": False, "page": 2, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "BUY"},
    {"proMerchantAds": False, "page": 2, "rows": 20, "payTypes": [], "countries": [], "publisherType": None, "asset": "USDT", "fiat": "MMK", "tradeType": "SELL"}
]

# Fetch and combine data
data = []
for payload in payloads:
    data.extend(fetch_data(payload))

# Process data into a DataFrame
if data:
    result = [dict(pair for d1 in d.values() for pair in d1.items()) for d in data]
    x = list(map(lambda x: x.get("price", 0), result))
    y = list(map(lambda y: y.get("tradableQuantity", 0), result))
    z = list(map(lambda z: z.get("tradeType", ""), result))
    combineddata = [{'price': price, 'limit': limit, 'buysell': buysell} for price, limit, buysell in zip(x, y, z)]
    df = pd.DataFrame(data=combineddata)

    # Convert columns to appropriate types
    df.price = df.price.astype("float")
    df.limit = df.limit.astype("float")
    df.buysell = df.buysell.astype("str")

    # Filter outliers (optional step, adjust as needed)
    price_lower_quantile = df.price.quantile(0.05)
    price_upper_quantile = df.price.quantile(0.95)
    df = df[(df.price >= price_lower_quantile) & (df.price <= price_upper_quantile)]

    buy = df[df.buysell == 'BUY']
    sell = df[df.buysell == 'SELL']

    # Function to round numbers to the nearest 25
    def round_25(number):
        return 25 * round(number / 25)

    # Rounding for x-axis ticks
    min_round = round_25(df.price.min())
    max_round = round_25(df.price.max())

    # Plotting
    fig, ax = plt.subplots()
    ax.set_title(f"Last update: {current_time}")
    sns.ecdfplot(x="price", weights="limit", stat="count", data=sell, ax=ax)
    sns.ecdfplot(x="price", weights="limit", stat="count", complementary=True, data=buy, ax=ax)
    sns.scatterplot(x="price", y="limit", hue="buysell", data=df, ax=ax, s=50, alpha=0.7)

    ax.set_xlabel("Price (MMK)")
    ax.set_ylabel("Tradable Quantity (Depth)")
    ax.set_yscale('log')
    ax.set_xticks(np.arange(min_round, max_round + 1, 25))
    ax.set_yticks([100, 250, 500, 1000, 2000, 5000, 10000, 50000, 100000, 200000, 500000, 1000000], 
                  labels=[100, 250, 500, "1k", "2k", "5k", "10k", "50k", "100k", "200k", "500k", "1M"])

    # Adding annotations for key points
    for i in range(len(df)):
        if df.iloc[i]['limit'] > 100000:
            ax.annotate(f"{df.iloc[i]['limit']}", (df.iloc[i]['price'], df.iloc[i]['limit']), textcoords="offset points", xytext=(0,10), ha='center')

    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write("No data available to display.")
