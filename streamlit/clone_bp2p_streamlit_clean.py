import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

######## start LOCAL TIME #####

import pytz
import requests

def get_timezone_from_ip():
    try:
        # Get the user's IP information
        response = requests.get('https://ipinfo.io')
        data = response.json()
        timezone = data['timezone']
        return timezone
    except Exception as e:
        # Default to UTC if there's an issue
        st.write(f"Error fetching timezone: {e}")
        return 'UTC'

# Get the local timezone based on the user's IP
local_tz_str = get_timezone_from_ip()
local_tz = pytz.timezone(local_tz_str)

# Get the current time in UTC
now_utc = datetime.now(pytz.utc)

# Convert the current UTC time to local time
now_local = now_utc.astimezone(local_tz)

# Format the local time
current_time = now_local.strftime("%d-%b-%Y %H:%M:%S GMT %z")

# Display the formatted time
# st.write(f"Last update: {current_time}")

############### END LOCAL TIME ##########

# Function to round numbers to the nearest 25
def round_25(number):
    return 25 * round(number / 25)

# Streamlit App Title
st.title('BinanceP2P USDT-MMK market')

# Display Converted Local Time
# st.write(f"Last update : {current_time}")

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
#This step removes the prices that fall outside the 5th and 95th percentiles, which helps in focusing on the central distribution of prices.
price_lower_quantile = df.price.quantile(0.05)
price_upper_quantile = df.price.quantile(0.95)
df = df[(df.price >= price_lower_quantile) & (df.price <= price_upper_quantile)]

buy = df.loc[df.buysell == 'BUY']
sell = df.loc[df.buysell == 'SELL']

# Rounding for x-axis ticks
min_round = round_25(min(df.price))
max_round = round_25(max(df.price))

# Plotting
fig, ax = plt.subplots()
ax.set_title(f"Last update: {current_time}")
sns.ecdfplot(x="price", weights="limit", stat="count", data=sell, ax=ax)
sns.ecdfplot(x="price", weights="limit", stat="count", complementary=True, data=buy, ax=ax)
sns.scatterplot(x="price", y="limit", hue="buysell", data=df, ax=ax, s=50, alpha=0.7) 
# Adjusting the point size (s=50) and transparency (alpha=0.7) helps in better visualizing overlapping points.


ax.set_xlabel("Price (mmk)")
ax.set_ylabel("Tradable Quantity (Depth)")
ax.set_yscale('log')
ax.set_xticks(np.arange(min_round, max_round + 1, 25))
ax.set_yticks([100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000], 
              [100, 250, 500, "1k", "2.5k", "5k", "10k", "25k", "50k", "100k", "250k", "500k", "1M"])

# Rotate x-axis tick labels by 90 degrees counter clockwise
ax.set_xticklabels(ax.get_xticks(), rotation=90)

# Adding annotations for key points
for i in range(len(df)):
    if df.iloc[i]['limit'] > 100000:
        ax.annotate(f"{df.iloc[i]['limit']}", (df.iloc[i]['price'], df.iloc[i]['limit']), textcoords="offset points", xytext=(0,10), ha='center')


# Display the plot in Streamlit
st.pyplot(fig)
