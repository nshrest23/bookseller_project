from flask import Flask
from routes import book_blueprint
from models import db, Book, init_app
from flask_migrate import Migrate


app = Flask(__name__)


app.config['SECRET_KEY'] = 'tZp5bR6prl5hkpxCu7I8lA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.db'

app.register_blueprint(book_blueprint)
init_app(app)

migrate = Migrate(app, db)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)