import sqlite3
from datetime import datetime

DB_FILE = "trading_journal.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT,
            entry REAL,
            tp REAL,
            sl REAL,
            score REAL,
            lot REAL,
            risk_amount REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_signal_to_db(signal_payload, action, score, risk_calc):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO signals (timestamp, action, entry, tp, sl, score, lot, risk_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        action,
        signal_payload.get("entry"),
        signal_payload.get("tp"),
        signal_payload.get("sl"),
        score,
        risk_calc.get("lot", 0.0),
        risk_calc.get("risk_amount", 0.0)
    ))
    conn.commit()
    conn.close()
