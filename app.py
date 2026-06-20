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


# Ã°Å¸â€Â¢ Generate next token
def get_next_token():
    cur = conn.cursor()
    cur.execute("SELECT MAX(token) FROM orders;")
    result = cur.fetchone()[0]
    return (result + 1) if result else 1


# Ã°Å¸â€œÅ  Get queue length
def get_queue_length():
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE status='Pending';")
    return cur.fetchone()[0]

def normalize_order_status(status):
    if not status:
        return 'Unknown'

    value = str(status).strip()
    if value.lower() == 'prepaing':
        return 'Preparing'

    return value


def build_staff_dashboard_payload():
    cur = conn.cursor()
    cur.execute(
        """
        SELECT token, item, quantity, status, phone, email
        FROM orders
        ORDER BY token DESC, item ASC
        """
    )
    rows = cur.fetchall()

    grouped = {}
    active_statuses = {'Pending', 'Preparing'}
    ready_statuses = {'Ready', 'Completed'}

    for token, item, quantity, status, phone, email in rows:
        token_key = str(token)
        normalized_status = normalize_order_status(status)

        if token_key not in grouped:
            grouped[token_key] = {
                'token': token,
                'status': normalized_status,
                'phone': phone,
                'email': email,
                'items': []
            }

        group = grouped[token_key]
        group['phone'] = group['phone'] or phone
        group['email'] = group['email'] or email
        group['items'].append({
            'name': item,
            'qty': quantity
        })

        if normalized_status in active_statuses:
            group['status'] = normalized_status

    def sort_key(order):
        try:
            return int(order['token'])
        except (TypeError, ValueError):
            return 0

    orders = sorted(grouped.values(), key=sort_key, reverse=True)
    active_orders = [order for order in orders if order['status'] in active_statuses]
    pending_orders = [order for order in orders if order['status'] == 'Pending']
    completed_orders = [order for order in orders if order['status'] in ready_statuses]
    oldest_active = min(active_orders, key=sort_key) if active_orders else None

    if active_orders:
        alert_title = f"{len(active_orders)} live order{'s' if len(active_orders) != 1 else ''} waiting"
        alert_subtitle = f"Oldest open token #{oldest_active['token']}"
        alert_tone = 'warning'
    else:
        alert_title = 'Kitchen is caught up'
        alert_subtitle = 'No active tickets right now'
        alert_tone = 'calm'

    return {
        'stats': {
            'active_orders': len(active_orders),
            'pending_orders': len(pending_orders),
            'completed_orders': len(completed_orders),
            'alert_count': len(active_orders)
        },
        'alert': {
            'title': alert_title,
            'subtitle': alert_subtitle,
            'tone': alert_tone
        },
        'orders': orders
    }

def build_user_orders_payload(email=None, phone=None):
    cur = conn.cursor()

    cur.execute("SELECT name, price FROM menu")
    menu_prices = {str(name).strip().lower(): float(price or 0) for name, price in cur.fetchall()}

    filters = []
    params = []

    if email:
        filters.append("LOWER(COALESCE(email, '')) = %s")
        params.append(email.strip().lower())

    if phone:
        filters.append("COALESCE(phone, '') = %s")
        params.append(phone.strip())

    if filters:
        query = f"""
            SELECT token, item, quantity, status, phone, email
            FROM orders
            WHERE {' OR '.join(filters)}
            ORDER BY token DESC, item ASC
        """
        cur.execute(query, params)
        rows = cur.fetchall()
    else:
        rows = []

    grouped = {}

    for token, item, quantity, status, row_phone, row_email in rows:
        token_key = str(token)
        normalized_status = normalize_order_status(status)
        price = menu_prices.get(str(item).strip().lower(), 0)

        if token_key not in grouped:
            grouped[token_key] = {
                'token': token,
                'status': normalized_status,
                'phone': row_phone,
                'email': row_email,
                'items': [],
                'subtotal': 0.0
            }

        group = grouped[token_key]
        group['phone'] = group['phone'] or row_phone
        group['email'] = group['email'] or row_email
        group['items'].append({
            'name': item,
            'qty': quantity,
            'price': price,
            'subtotal': price * quantity
        })
        group['subtotal'] += price * quantity

        if normalized_status != 'Unknown':
            group['status'] = normalized_status

    def sort_key(order):
        try:
            return int(order['token'])
        except (TypeError, ValueError):
            return 0

    orders = sorted(grouped.values(), key=sort_key, reverse=True)
    live_orders = orders[:2]
    archive_orders = orders[2:]

    return {
        'profile': {
            'email': email,
            'phone': phone,
            'display_name': (email.split('@')[0].replace('.', ' ').replace('_', ' ').title() if email else 'Student')
        },
        'stats': {
            'live_count': len(live_orders),
            'archive_count': len(archive_orders),
            'total_count': len(orders)
        },
        'live_orders': live_orders,
        'archive_orders': archive_orders,
        'orders': orders
    }


@app.route('/user-orders', methods=['GET'])
def user_orders():
    email = request.args.get('email', '').strip()
    phone = request.args.get('phone', '').strip()
    return jsonify(build_user_orders_payload(email=email, phone=phone))


# dynamic menu
@app.route('/menu', methods=['GET'])
def get_menu():
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, category, image_url FROM menu WHERE available = TRUE;")
    items = cur.fetchall()

    menu = []
    for item in items:
        menu.append({
            "id": item[0],
            "name": item[1],
            "price": item[2],
            "cat": item[3],
            "image_url": item[4]
        })

    return jsonify(menu)


@app.route('/staff-dashboard-data', methods=['GET'])
def staff_dashboard_data():
    return jsonify(build_staff_dashboard_payload())


# Ã°Å¸Å¸Â¢ Place Order API
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

     # Get customer's phone number
    cur.execute(
        "SELECT phone FROM orders WHERE token=%s LIMIT 1",
        (token,)
    )

    phone = cur.fetchone()[0]

    # Send data to n8n
    requests.post(
        "https://canteeniq.app.n8n.cloud/webhook/order-ready",
        json={
            "phone": phone,
            "token": token
        }
    )

    conn.commit()

    try:
        requests.get(
            f"http://10.65.48.13/ready?token={token}",
            timeout=3
        )

        print(f"Sent token {token} to NodeMCU")

    except Exception as e:
        print("NodeMCU Error:", e)

    return jsonify({
        "success": True,
        "message": "Order marked as Ready"
    })


# Ã°Å¸â€Å’ Get Ready Tokens (for hardware)
@app.route('/ready-tokens', methods=['GET'])
def ready_tokens():
    cur = conn.cursor()
    cur.execute(
        "SELECT token FROM orders WHERE status='Ready'"
    )
    tokens = [row[0] for row in cur.fetchall()]

    return jsonify({"tokens": tokens})


# Ã°Å¸â€œâ€¹ Get Pending Orders (kitchen)
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
