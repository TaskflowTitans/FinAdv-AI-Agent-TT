import sqlite3
import pandas as pd

DB_NAME = "expenses.db"

def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        amount REAL,
        category TEXT,

        date TEXT,
        time TEXT,

        description TEXT,

        sender TEXT,
        upi_id TEXT,

        bank_name TEXT,

        transaction_id TEXT,

        receipt_type TEXT,

        confidence_score REAL
    )
    """)

    conn.commit()
    conn.close()


def insert_transaction(data):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions (
        amount,
        category,
        date,
        time,
        description,
        sender,
        upi_id,
        bank_name,
        transaction_id,
        receipt_type,
        confidence_score
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("amount"),
        data.get("category"),
        data.get("date"),
        data.get("time"),
        data.get("description"),
        data.get("sender"),
        data.get("upi_id"),
        data.get("bank_name"),
        data.get("transaction_id"),
        data.get("receipt_type"),
        data.get("confidence_score")
    ))

    conn.commit()
    conn.close()


def get_all_transactions():
    conn = connect()

    df = pd.read_sql_query("SELECT * FROM transactions", conn)

    conn.close()
    return df


def delete_all():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions")

    conn.commit()
    conn.close()