from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app import limiter
from flask import send_from_directory, current_app

user_bp = Blueprint('users', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    result, status = UserService.get_profile(user_id)
    return jsonify(result), status

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
@limiter.limit("5 per minute")
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    username = str(data.get('username', '')).strip()
    if username and not (2 <= len(username) <= 50):
        return jsonify({"error": "Имя должно быть от 2 до 50 символов"}), 400

    result, status = UserService.update_profile(user_id, data)
    return jsonify(result), status

@user_bp.route('/avatar', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def upload_avatar():
    user_id = get_jwt_identity()
    if 'avatar' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "Выберите файл для загрузки"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "Разрешены только форматы JPG и PNG"}), 400

    result, status = UserService.upload_avatar(user_id, file)
    return jsonify(result), status

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    result, status = UserService.get_stats(user_id)
    return jsonify(result), status

@user_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    result, status = UserService.get_learning_progress(user_id, page=page)
    return jsonify(result), status

@user_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    result, status = UserService.get_activity_history(user_id, page=page)
    return jsonify(result), status


@user_bp.route('/avatar/<filename>')
@jwt_required()
def get_avatar(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
