from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
CORS(app)

# Connect to Supabase (PostgreSQL)
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.autocommit = True


# 🔢 Generate next token
def get_next_token():
    cur = conn.cursor()
    cur.execute("SELECT MAX(token) FROM orders;")
    result = cur.fetchone()[0]
    return (result + 1) if result else 1


# 📊 Get queue length
def get_queue_length():
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE status='Pending';")
    return cur.fetchone()[0]

# dynamic menu
@app.route('/menu', methods=['GET'])
def get_menu():
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, category FROM menu WHERE available = TRUE;")
    items = cur.fetchall()

    menu = []
    for item in items:
        menu.append({
            "id": item[0],
            "name": item[1],
            "price": item[2],
            "cat": item[3]   # IMPORTANT: match frontend (cat)
        })

    return jsonify(menu)


# 🟢 Place Order API
@app.route('/order', methods=['POST'])
def place_order():
    data = request.json
    items = data['items']

    token = get_next_token()
    queue_length = get_queue_length()

    # Simple ETA (1 min per order)
    eta = queue_length * 5  

    cur = conn.cursor()
    for i in items:
        cur.execute(
            "INSERT INTO orders (token, item, quantity, status) VALUES (%s, %s, %s, %s)",
            (token, i['name'], i['qty'], 'Pending')
    )

    return jsonify({
        "token": token,
        "queue_length": queue_length,
        "estimated_time": eta
    })


# 🔴 Mark Order Ready
@app.route('/mark-ready', methods=['POST'])
def mark_ready():
    token = request.json['token']

    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET status='Ready' WHERE token=%s",
        (token,)
    )

    return jsonify({"message": "Order marked as Ready"})


# 🔌 Get Ready Tokens (for hardware)
@app.route('/ready-tokens', methods=['GET'])
def ready_tokens():
    cur = conn.cursor()
    cur.execute(
        "SELECT token FROM orders WHERE status='Ready'"
    )
    tokens = [row[0] for row in cur.fetchall()]

    return jsonify({"tokens": tokens})


# 📋 Get Pending Orders (kitchen)
@app.route('/orders', methods=['GET'])
def get_orders():
    cur = conn.cursor()
    cur.execute(
        "SELECT token, item, quantity FROM orders WHERE status='Pending'"
    )
    orders = cur.fetchall()

    return jsonify(orders)


if __name__ == '__main__':
    app.run(debug=True)