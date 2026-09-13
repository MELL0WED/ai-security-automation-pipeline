import sqlite3

def search_products(name):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name = '" + name + "'")
    return cursor.fetchall()
