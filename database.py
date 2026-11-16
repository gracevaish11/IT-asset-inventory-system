"""
database.py

Handles the SQLite connection and table creation for the
IT Asset Inventory System. All other modules go through
get_connection() to talk to the database.
"""

import sqlite3
import os

DB_NAME = "asset_inventory.db"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)


def get_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the assets table if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT NOT NULL UNIQUE,
            asset_type TEXT NOT NULL,
            manufacturer TEXT,
            model TEXT,
            serial_number TEXT,
            operating_system TEXT,
            os_version TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            assigned_to TEXT,
            department TEXT,
            location TEXT,
            purchase_date TEXT,
            warranty_expiry TEXT
        )
        """
    )
    conn.commit()
    conn.close()
