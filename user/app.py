from flask import Flask
from flask.sessions import SecureCookieSessionInterface
import models
from routes import user_blueprint
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'me4tqAiH7smuQlxCt2gBEg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'

models.init_app(app)

app.register_blueprint(user_blueprint)
login_manager = LoginManager(app)
migrate = Migrate(app, models.db)

# @app.route('/')
# def index():
#     return "hello!"

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.filter_by(id=user_id).first()

@login_manager.request_loader
def load_user_from_request(request):
    # first, try to login using the api_key url arg
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        user = models.User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    return None

class CustomSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session from API requests."""
    def save_session(self, *args, **kwargs):
        if g.get('login_via_request'):
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)