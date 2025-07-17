import sqlite3

def init_db():
    conn = sqlite3.connect("logements.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            price TEXT,
            area TEXT,
            link TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def get_all_logement_links():
    conn = sqlite3.connect("logements.db")
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM logements")
    rows = cursor.fetchall()
    conn.close()
    return set(row[0] for row in rows)

def insert_logement(name, address, price, area, link):
    conn = sqlite3.connect("logements.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO logements (name, address, price, area, link) VALUES (?, ?, ?, ?, ?)",
                       (name, address, price, area, link))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # already exists
    conn.close()

def delete_missing_logements(current_links):
    conn = sqlite3.connect("logements.db")
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM logements")
    db_links = set(row[0] for row in cursor.fetchall())

    to_delete = db_links - current_links
    for link in to_delete:
        cursor.execute("DELETE FROM logements WHERE link = ?", (link,))
    conn.commit()
    conn.close()
