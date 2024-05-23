import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Function to fetch historical data from the database
def get_historical_data():
    conn = sqlite3.connect('binance_data.db')
    df = pd.read_sql_query("SELECT * FROM p2p_data", conn)
    conn.close()
    return df

# Fetch data and show historical chart
st.title('Historical Binance P2P Data Visualization')

df = get_historical_data()

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=df, x='timestamp', y='price', hue='buysell', ax=ax)
ax.set_title('Price Over Time')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Price')

# Display the plot in Streamlit
st.pyplot(fig)
