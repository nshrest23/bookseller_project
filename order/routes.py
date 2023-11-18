from flask import Blueprint, jsonify, request, make_response
from models import db, Order, OrderItem
import requests

order_blueprint = Blueprint('order_api_routes', __name__, url_prefix="/api/order")
USER_API_URL = 'http://user-service-c:5001/api/user'

def get_user(api_key):
    headers = {
        "Authorization": api_key
    }
    response = requests.get(USER_API_URL, headers=headers)
    if response.status_code != 200:
        return {'message': "User Not Authorized"}
    else:
        user = response.json()
        return user

@order_blueprint.route('/', methods=['GET'])
def get_order():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'message': 'User not Logged in'}), 401
    response = get_user(api_key)  
    user = response.get('result')
    if not response.get('result'):
        return jsonify({'message': 'User not Logged in'}), 401
    
    open_order = Order.query.filter_by(user_id=user['id'], is_open=1).first()
    if open_order:
        return jsonify({'result': open_order.serialize()}), 200
    else: 
        return jsonify({'message': "No Open Orders"})

@order_blueprint.route('/all', methods=['GET'])
def all_orders():
    all_orders = Order.query.all()
    result = [order.serialize() for order in all_orders]
    return jsonify(result), 200

@order_blueprint.route('/add-item', methods=['POST'])
def add_order_item():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'message': 'User not Logged in'}), 401
    response = get_user(api_key)
    if not response.get('result'):
        return jsonify({'message': 'User not Logged in'}), 401
    user = response.get('result')
    book_id = int(request.form['book_id'])
    quantity = int(request.form['quantity'])
    user_id = user['id']
    open_order = Order.query.filter_by(user_id=user_id, is_open=1).first()
    if not open_order:
        open_order = Order()
        open_order.is_open = True
        open_order.user_id = user_id

        order_item = OrderItem(book_id=book_id, quantity=quantity)
        open_order.order_items.append(order_item)
    else:
        found = False
        for item in open_order.order_items:
            if item.book_id == book_id:
                item.quantity += quantity
                found = True
        if not found:
            order_item = OrderItem(book_id=book_id, quantity=quantity)
            open_order.order_items.append(order_item)

    db.session.add(open_order)
    db.session.commit()

    return jsonify({'result': open_order.serialize()})

@order_blueprint.route('/checkout', methods=['POST'])
def checkout():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'message': 'User not Logged in'}), 401
    response = get_user(api_key)  
    user = response.get('result')
    if not user:
        return jsonify({'message': 'User not Logged in'}), 401
    open_order = Order.query.filter_by(user_id=user['id'], is_open=1).first()
    if open_order:
        open_order.is_open = False
        print(open_order)
        db.session.add(open_order)
        db.session.commit()
        return jsonify({'result': open_order.serialize()}), 200
    else:
        return jsonify({'message': "No Open Orders"})
    
