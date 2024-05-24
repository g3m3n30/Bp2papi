import numpy as np
import requests
import pandas as pd
import gspread
from datetime import datetime

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

# print(type(df))
# print(df.head)

# Get the highest buy price and its limit
highest_buy_row = buy.loc[buy['price'].idxmax()]
highest_buy_price = highest_buy_row['price']
highest_buy_limit = highest_buy_row['limit']

# Get the lowest sell price and its limit
lowest_sell_row = sell.loc[sell['price'].idxmin()]
lowest_sell_price = lowest_sell_row['price']
lowest_sell_limit = lowest_sell_row['limit']

# Get the current date and time
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#print("buy:", highest_buy_price,"mmk, amount: ",highest_buy_limit, "usd, sell:", lowest_sell_price,"mmk, amount: ",lowest_sell_limit, "usd")

product={'date':current_datetime,'buy':highest_buy_price,'buy_amount':highest_buy_limit,'sell':lowest_sell_price,'sell_amount':lowest_sell_limit}

print(product)

def output(product):
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open('Binance USDT-MMK tracker').sheet1
    sh.append_row([str(product['date']), str(product['buy']), float(product['sell']), float(product['buy_amount']), float(product['sell_amount'])])
    return
output(product)


