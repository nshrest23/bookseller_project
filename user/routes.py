from flask import Blueprint, jsonify, request, make_response
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user

user_blueprint = Blueprint('user_api_routes', __name__, url_prefix="/api/user")
# @user_blueprint.route('/')
# def index():
#     return "Hello"

@user_blueprint.route('/all', methods=['GET'])
def get_all_users():
    all_user = User.query.all()
    result = [user.serialize() for user in all_user]
    response = {
        'message': 'Returning All users',
        'result': result,
    }
    return jsonify(response)

@user_blueprint.route('/create', methods=['POST'])
def create_user():
    try:
        user = User()
        user.username = request.form["username"]
        user.password = generate_password_hash(request.form["password"], method="pbkdf2")
        user.is_active = True

        db.session.add(user)
        db.session.commit()
        
        response = {'message': 'User Created Successfully', 'result': user.serialize()}
    except Exception as e:
        print(str(e))
        response = {'message': 'Error Creating User'}

    return jsonify(response) 

@user_blueprint.route('/login', methods = ['POST'])
def user_login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return make_response(jsonify({'message': 'User Does Not Exists'}), 401)
    if check_password_hash(user.password, password):
        user.update_api_key()
        db.session.commit()
        login_user(user)
        response = {'message': "user logged in succefully", 'api_key': user.api_key}
        return make_response(jsonify(response), 200)
    response = {'message': 'Access Denied'}
    return make_response(jsonify(response), 401)

@user_blueprint.route('/logout', methods = ['POST'])
def user_logout():
    if current_user.is_authenticated:
        logout_user()
        return make_response(jsonify({'message': 'User Logged Out Successfully'}), 200)
    return make_response(jsonify({'message': 'No User Logged In'}), 401)

@user_blueprint.route('/<username>/exist', methods = ['GET'])
def user_exists(username):
    user = User.query.filter_by(username = username).first()
    if user:
        return make_response(jsonify({'result': True}), 200)
    return make_response(jsonify({'result': False}), 404)
    
@user_blueprint.route('/', methods = ['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return make_response(jsonify({'result': current_user.serialize()}), 200)
    else:
        return make_response(jsonify({'message': 'No User Logged In'}), 401)