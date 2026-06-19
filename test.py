import psycopg2

conn = psycopg2.connect("postgresql://postgres:Smartcanteen%401234@db.qtowwoslngucegekgcol.supabase.co:5432/postgres")
cur = conn.cursor()

cur.execute("""
INSERT INTO orders (item, quantity, status)
VALUES (%s, %s, %s)
RETURNING token;
""", ('Samosa', 2, 'Pending'))

token = cur.fetchone()[0]
print(token)

conn.commit()  # VERY IMPORTANT

# 🔍 FETCH DATA
cur.execute("SELECT * FROM orders;")
print(cur.fetchall())

cur.close()
conn.close()