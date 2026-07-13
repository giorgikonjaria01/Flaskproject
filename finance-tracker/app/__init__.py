from flask import Flask
from app.extensions import db
from flask_migrate import Migrate
from app.utils import format_currency

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate = Migrate(app, db)

    from app import models
    from app.auth.routes import auth_bp
    from app.api.routes import api_bp
    from app.main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)

    app.jinja_env.filters['currency'] = format_currency

    return app