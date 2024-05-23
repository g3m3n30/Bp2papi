import requests
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler

# Function to fetch and store data
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
    
    # Store data in database
    conn = sqlite3.connect('binance_data.db')
    cursor = conn.cursor()
    for entry in combineddata:
        cursor.execute("INSERT INTO p2p_data (price, limit, buysell) VALUES (?, ?, ?)", (entry['price'], entry['limit'], entry['buysell']))
    conn.commit()
    conn.close()

# Scheduler to fetch data every few minutes
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_data, 'interval', minutes=5)
scheduler.start()

# Fetch initial data
fetch_and_store_data()

# Keep the script running
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
