from flask import Flask, app, render_template
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
    from app.auth.decorators import get_current_user

    @app.context_processor
    def inject_user():
        return dict(get_current_user=get_current_user)
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    # @app.errorhandler(500)
    # def server_error(e):
    #     return render_template('errors/500.html'), 500
    
    return app