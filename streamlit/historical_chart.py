import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Function to fetch historical data from the database
def fetch_historical_data():
    conn = sqlite3.connect('binance_p2p.db')
    df = pd.read_sql_query("SELECT * FROM p2p_data", conn)
    conn.close()
    return df

# Fetch historical data
historical_df = fetch_historical_data()

# Convert timestamp to datetime
historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'])

# Streamlit App Title
st.title('Historical BinanceP2P USDT-MMK Prices')

# Plot historical data
fig, ax = plt.subplots()
sns.lineplot(x='timestamp', y='price', hue='buysell', data=historical_df, ax=ax)
ax.set_title("Historical P2P Prices")
ax.set_xlabel("Timestamp")
ax.set_ylabel("Price (MMK)")
plt.xticks(rotation=45)
st.pyplot(fig)
