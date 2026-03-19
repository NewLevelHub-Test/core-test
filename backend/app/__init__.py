import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import config_by_name

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.lesson_routes import lesson_bp
    from app.routes.test_routes import test_bp
    from app.routes.game_routes import game_bp
    from app.routes.analysis_routes import analysis_bp
    from app.routes.photo_routes import photo_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.roadmap_routes import roadmap_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(lesson_bp, url_prefix='/api/lessons')
    app.register_blueprint(test_bp, url_prefix='/api/tests')
    app.register_blueprint(game_bp, url_prefix='/api/games')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(photo_bp, url_prefix='/api/photo')
    app.register_blueprint(roadmap_bp, url_prefix='/api/roadmap')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    import logging
    from flask import jsonify

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "Ресурс не найден"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Server Error: {error}")
        return jsonify({"error": "Internal Server Error", "message": "Внутренняя ошибка сервера"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Unexpected error occurred")
        return jsonify({"error": "Unexpected Error", "message": "Что-то пошло не так"}), 500

    return app
