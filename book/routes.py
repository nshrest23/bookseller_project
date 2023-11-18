from flask import Blueprint, request, jsonify, make_response
from models import Book, db

book_blueprint = Blueprint('book_api_routes', __name__, url_prefix="/api/book")

@book_blueprint.route('/all', methods=["GET"])
def get_all_books():
    all_books = Book.query.all()
    result = [book.serialize() for book in all_books ]
    response = {'message': 'Returning All Books', 'result': result}

    return jsonify(response)

@book_blueprint.route('/create', methods=['POST'])
def create_book():
    try:
        book = Book()
        book.name = request.form['name']
        book.slug = request.form['slug']
        book.price = request.form['price']
        book.image = request.form['image']

        db.session.add(book)
        db.session.commit()
        response = {'message': 'Books Created Successfully', 'result': book.serialize()}
    except Exception as e:
        print(str(e))
        response = {'message': 'Creating Book Failed'}
    return jsonify(response)

@book_blueprint.route('/<slug>', methods=['GET'])
def book_detail(slug):
    book = Book.query.filter_by(slug=slug).first()
    if book: 
        response = {'result': book.serialize()}
    else:
        response = {'message': 'No Book Found'}
    return jsonify(response)