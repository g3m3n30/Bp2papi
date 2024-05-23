import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('binance_data.db')
cursor = conn.cursor()

# Create table to store buy and sell data
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
