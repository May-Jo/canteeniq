from flask import Flask, request, jsonify
import psycopg2
import razorpay
import os
from dotenv import load_dotenv
from flask_cors import CORS
import requests

razorpay_client = razorpay.Client(auth=("rzp_test_Ss0NUzhn05UPcG", "GETSorkQI6gVee60PwieW91S"))

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

@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.json
    cart = data['cart']

    total = sum(item['price'] * item['qty'] for item in cart)

    order = razorpay_client.order.create({
        "amount": int(total * 100),
        "currency": "INR"
    })

    return jsonify({
        "amount": int(total * 100),
        "razorpay_order_id": order['id']
    })

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    data = request.json
    cart = data['cart']
    email = data['email']
    phone = data['phone']

    token = get_next_token()

    for item in cart:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO orders
            (token, item, quantity, status, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                token,
                item['name'],
                item['qty'],
                'Pending',
                phone,
                email
            )
        )
    queue_length = get_queue_length()
    eta = queue_length * 5

    return jsonify({
        "token": token,
        "estimated_time": eta
    })


@app.route('/mark-ready', methods=['POST'])
def mark_ready():

    token = request.json['token']

    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET status='Ready' WHERE token=%s",
        (token,)
    )

    conn.commit()

    try:
        requests.get(
            f"http://192.168.1.20/ready?token={token}",
            timeout=3
        )

        print(f"Sent token {token} to NodeMCU")

    except Exception as e:
        print("NodeMCU Error:", e)

    return jsonify({
        "success": True,
        "message": "Order marked as Ready"
    })


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