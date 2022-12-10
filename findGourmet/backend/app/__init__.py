from flask import Flask

# from flask_bootstrap import Bootstrap
# from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config
from flask_cors import CORS
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_name="default"):
    app = Flask(__name__)   
    cors = CORS(app, supports_credentials=True ,resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
 
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    Migrate(app, db, render_as_batch=False)

    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")
    api_blueprint._got_registered_once = False  # 消除警告
    return app
