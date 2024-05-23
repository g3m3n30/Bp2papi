import sqlite3

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

