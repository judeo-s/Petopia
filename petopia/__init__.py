import os


# Flask instance
from flask import Flask, session

app = Flask(__name__, static_folder='templates/static', template_folder='templates')
app.app_context().push()


# Flask Login
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel

babel = Babel(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
PATH = os.path.dirname(__file__)

# Flask database
from flask_sqlalchemy import SQLAlchemy

app.config['SECRET_KEY'] = 'jhgeut387tr3287t87tuygfuy287t783t8'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(os.getcwd(), 'sqlite.db')
db = SQLAlchemy(app)


# Flask blueprints
from petopia.auth.routes import auth
from petopia.shop.routes import shop, Cart

app.register_blueprint(auth)
app.register_blueprint(shop)


@app.context_processor
def cart_context():
    cart_obj = Cart(session)
    return dict(cart_context=cart_obj)


# Loading user from session
from petopia.auth.models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE SUPERUSER
import click
from flask.cli import with_appcontext

@click.command(name="createsuperuser")
@with_appcontext
@click.argument("username", nargs=1)
@click.argument("password", nargs=1)
def create_superuser(username, password): # flask createsuperuser name pasword
    user = User(username=username, hash_password=password, is_superuser=True)
    db.session.add(user)
    db.session.commit()



# CSRF
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)


# COOKIE
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=864000
)

with app.app_context():
    db.create_all()
app.cli.add_command(create_superuser)

# Flask admin
from petopia.mgmt.models import admin