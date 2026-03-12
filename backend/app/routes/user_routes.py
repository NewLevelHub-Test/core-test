from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService

user_bp = Blueprint('users', __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    result, status = UserService.get_profile(user_id)
    return jsonify(result), status


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status = UserService.update_profile(user_id, data)
    return jsonify(result), status


@user_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()
    if 'avatar' not in request.files:
        return jsonify({'error': 'Файл не загружен'}), 400
    result, status = UserService.upload_avatar(user_id, request.files['avatar'])
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
    result, status = UserService.get_learning_progress(user_id)
    return jsonify(result), status


@user_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity():
    user_id = get_jwt_identity()
    result, status = UserService.get_activity_history(user_id)
    return jsonify(result), status
