"""
Скрипт для создания базы данных рецептов Эпплджек.

Автор: MADAO81
Версия: 1.0
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "recipes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            tip TEXT,
            source TEXT DEFAULT 'Эпплджек'
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON recipes (category)")

    conn.commit()
    conn.close()
    print(f"✅ База данных рецептов создана: {DB_PATH}")

if __name__ == "__main__":
    init_db()
