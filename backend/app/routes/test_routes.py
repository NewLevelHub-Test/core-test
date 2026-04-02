from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.test_service import TestService
from app import limiter

test_bp = Blueprint('tests', __name__)

@test_bp.route('/', methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_tests():
    page = request.args.get('page', 1, type=int) 
    result, status = TestService.get_tests(page=page)
    return jsonify(result), status

@test_bp.route('/attempts', methods=['GET'])
@jwt_required()
def get_attempts():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int) 
    result, status = TestService.get_user_attempts(user_id, page=page)
    return jsonify(result), status

@test_bp.route('/<int:test_id>', methods=['GET'])
@jwt_required()
def get_test(test_id):
    result, status = TestService.get_test(test_id)
    return jsonify(result), status

@test_bp.route('/<int:test_id>/start', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def start_test(test_id):
    user_id = get_jwt_identity()
    result, status = TestService.start_test(user_id, test_id)
    return jsonify(result), status

@test_bp.route('/<int:test_id>/submit', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")  # <--- ЛИМИТЕР ЗДЕСЬ
def submit_test(test_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    # Извлекаем ответы для валидации
    answers = data.get('answers')

    # Проверка: answers не должен быть None и должен быть либо списком [], либо словарем {}
    if answers is None or not isinstance(answers, (list, dict)):
        return jsonify({
            "error": "Validation Error", 
            "message": "Invalid answers format. Expected list or dict."
        }), 400

    # Передаем весь объект data в сервис, так как сервис сам внутри ищет ключ 'answers'
    result, status = TestService.submit_test(user_id, test_id, data)
    return jsonify(result), status


@test_bp.route('/attempts/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_attempt_detail(attempt_id):
    user_id = get_jwt_identity()
    result, status = TestService.get_attempt_detail(user_id, attempt_id)
    return jsonify(result), status

@test_bp.route('/level', methods=['GET'])
@jwt_required()
def get_level():
    user_id = get_jwt_identity()
    result, status = TestService.get_level_info(user_id)
    return jsonify(result), status