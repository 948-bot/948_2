import sqlite3
from datetime import datetime, timedelta

DB_FILE = "anti_spam.db"

def _init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cooldowns (
            action TEXT PRIMARY KEY,
            last_signal_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def check_anti_spam(action: str, price: float, cooldown_minutes: int = 30) -> bool:
    _init_db()
    now = datetime.now()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT last_signal_time FROM cooldowns WHERE action=?", (action,))
    row = c.fetchone()
    if row:
        last_time = datetime.fromisoformat(row[0])
        if now - last_time < timedelta(minutes=cooldown_minutes):
            conn.close()
            return False
    c.execute("REPLACE INTO cooldowns (action, last_signal_time) VALUES (?, ?)",
              (action, now.isoformat()))
    conn.commit()
    conn.close()
    return True
