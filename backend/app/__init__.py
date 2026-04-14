import os
import re
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

token_blocklist = set()


from app.config import config_by_name

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    if config_name == 'production':
        missing = [
            key for key in ('SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL')
            if not os.environ.get(key)
        ]
        if missing:
            raise RuntimeError(f"Missing required environment variables for production: {', '.join(missing)}")

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in token_blocklist
    limiter.storage_uri = app.config.get('RATELIMIT_STORAGE_URI', 'memory://')
    limiter.init_app(app)

    cors_origins = [
        origin.strip()
        for origin in app.config.get('CORS_ALLOWED_ORIGINS', '').split(',')
        if origin.strip()
    ]
    if not cors_origins:
        cors_origins = ["*"]

    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

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
    from app.routes.chat_routes import chat_bp



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
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    logging.basicConfig(level=logging.INFO)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "Ресурс не найден"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        return jsonify({"error": "Internal Server Error", "message": "Внутренняя ошибка сервера"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unexpected error occurred")
        return jsonify({"error": "Unexpected Error", "message": "Что-то пошло не так"}), 500

    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok"}), 200

    from app.models.analysis_cache import AnalysisCache

    from flask_limiter.errors import RateLimitExceeded



    @app.errorhandler(RateLimitExceeded)
    def handle_ratelimit_error(e):
        return jsonify({
            "error": "Too Many Requests",
            "message": "Вы отправляете запросы слишком часто. Подождите немного.",
            "limit": str(e.description)
        }), 429


    return app