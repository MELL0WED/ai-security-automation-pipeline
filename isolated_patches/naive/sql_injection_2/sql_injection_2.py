import sqlite3

def search_products(name):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    # Use parameterized query to prevent SQL injection
    cursor.execute("SELECT * FROM products WHERE name = ?", (name,))
    return cursor.fetchall()
