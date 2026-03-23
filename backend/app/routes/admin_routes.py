from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.admin.admin_service import AdminService
from app import limiter

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@jwt_required()
def check_admin():
    user_id = get_jwt_identity()
    if not AdminService.is_admin(user_id):
        return jsonify({'error': 'Доступ запрещён'}), 403

# --- Users ---

@admin_bp.route('/users', methods=['GET'])
@limiter.limit("30 per minute")
def get_users():
    page = request.args.get('page', 1, type=int)
    result, status = AdminService.get_all_users(page)
    return jsonify(result), status

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    result, status = AdminService.get_user_detail(user_id)
    return jsonify(result), status

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result, status = AdminService.delete_user(user_id)
    return jsonify(result), status

# --- Topics ---

@admin_bp.route('/topics', methods=['GET'])
def get_topics():
    result, status = AdminService.get_topics()
    return jsonify(result), status

@admin_bp.route('/topics', methods=['POST'])
def create_topic():
    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({'error': 'Название темы обязательно'}), 400
    result, status = AdminService.create_topic(data)
    return jsonify(result), status

@admin_bp.route('/topics/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Нет данных для обновления'}), 400
    result, status = AdminService.update_topic(topic_id, data)
    return jsonify(result), status

@admin_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    result, status = AdminService.delete_topic(topic_id)
    return jsonify(result), status

# --- Lessons ---

@admin_bp.route('/lessons', methods=['POST'])
def create_lesson():
    data = request.get_json() or {}
    if not data.get('title') or not data.get('topic_id'):
        return jsonify({'error': 'Заголовок и ID темы обязательны'}), 400
    result, status = AdminService.create_lesson(data)
    return jsonify(result), status

@admin_bp.route('/lessons/<int:lesson_id>', methods=['PUT'])
def update_lesson(lesson_id):
    data = request.get_json() or {}
    result, status = AdminService.update_lesson(lesson_id, data)
    return jsonify(result), status

@admin_bp.route('/lessons/<int:lesson_id>', methods=['DELETE'])
def delete_lesson(lesson_id):
    result, status = AdminService.delete_lesson(lesson_id)
    return jsonify(result), status

# --- Exercises ---

@admin_bp.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json() or {}
    if not data.get('lesson_id'):
        return jsonify({'error': 'lesson_id обязателен'}), 400
    result, status = AdminService.create_exercise(data)
    return jsonify(result), status

@admin_bp.route('/exercises/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    data = request.get_json() or {}
    result, status = AdminService.update_exercise(exercise_id, data)
    return jsonify(result), status

@admin_bp.route('/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    result, status = AdminService.delete_exercise(exercise_id)
    return jsonify(result), status

# --- Tests ---

@admin_bp.route('/tests', methods=['POST'])
def create_test():
    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({'error': 'Заголовок теста обязателен'}), 400
    result, status = AdminService.create_test(data)
    return jsonify(result), status

@admin_bp.route('/tests/<int:test_id>', methods=['PUT'])
def update_test(test_id):
    data = request.get_json() or {}
    result, status = AdminService.update_test(test_id, data)
    return jsonify(result), status

@admin_bp.route('/tests/<int:test_id>/questions', methods=['POST'])
def add_question(test_id):
    data = request.get_json() or {}
    if not data.get('text'):
        return jsonify({'error': 'Текст вопроса обязателен'}), 400
    result, status = AdminService.add_question(test_id, data)
    return jsonify(result), status

@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json() or {}
    result, status = AdminService.update_question(question_id, data)
    return jsonify(result), status

@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    result, status = AdminService.delete_question(question_id)
    return jsonify(result), status

# --- Stats ---

@admin_bp.route('/stats', methods=['GET'])
@limiter.limit("10 per minute")
def get_platform_stats():
    result, status = AdminService.get_platform_stats()
    return jsonify(result), status