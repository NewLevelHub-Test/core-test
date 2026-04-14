from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import re
from app.services.auth_service import AuthService
from app import limiter, token_blocklist

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return isinstance(email, str) and re.match(email_regex, email) is not None

def validate_password_strength(password):
    if len(password) < 6:
        return False, "Пароль должен быть не менее 6 символов"
    if not any(char.isdigit() for char in password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not any(char.isupper() for char in password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"
    return True, None

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip()
    phone = str(data.get('phone', '')).strip()
    password = str(data.get('password', ''))
    username = str(data.get('username', '')).strip()
    age = data.get('age')

    if not email and not phone:
        return jsonify({"error": "Validation Error", "message": "Укажите email или телефон"}), 400

    if email and not is_valid_email(email):
        return jsonify({"error": "Validation Error", "message": "Некорректный Email"}), 400

    if phone:
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not re.match(r'^\+?\d{10,15}$', cleaned_phone):
            return jsonify({"error": "Validation Error", "message": "Некорректный телефон"}), 400
        data['phone'] = cleaned_phone
    
    is_strong, error_msg = validate_password_strength(password)
    if not is_strong:
        return jsonify({"error": "Validation Error", "message": error_msg}), 400
    
    if not (3 <= len(username) <= 50):
        return jsonify({"error": "Validation Error", "message": "Имя от 3 до 50 символов"}), 400
    if age is not None and (not isinstance(age, int) or age < 5 or age > 12):
        return jsonify({"error": "Validation Error", "message": "Возраст должен быть от 5 до 12"}), 400

    result, status = AuthService.register(data)
    return jsonify(result), status

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', ''))

    if not email or not password:
        return jsonify({"error": "Validation Error", "message": "Заполните все поля"}), 400
        
    result, status = AuthService.login(data)
    return jsonify(result), status

@auth_bp.route('/send-code', methods=['POST'])
@limiter.limit("3 per minute")
def send_code():
    data = request.get_json() or {}
    phone = str(data.get('phone', '')).strip()
    import re as _re
    cleaned_phone = _re.sub(r'[\s\-\(\)]', '', phone)
    if not _re.match(r'^\+?\d{10,15}$', cleaned_phone):
        return jsonify({"error": "Validation Error", "message": "Неверный формат телефона"}), 400
        
    result, status = AuthService.send_sms_code(phone)
    return jsonify(result), status

@auth_bp.route('/verify-code', methods=['POST'])
@limiter.limit("5 per minute")
def verify_code():
    data = request.get_json() or {}
    phone = data.get('phone')
    code = data.get('code')
    if not phone or not code:
        return jsonify({"error": "Validation Error", "message": "Телефон и код обязательны"}), 400
    result, status = AuthService.verify_sms_code(phone, code)
    return jsonify(result), status

@auth_bp.route('/login-phone', methods=['POST'])
@limiter.limit("5 per minute")
def login_phone():
    data = request.get_json() or {}
    phone = data.get('phone')
    code = data.get('code')
    if not phone or not code:
        return jsonify({"error": "Validation Error", "message": "Телефон и код обязательны"}), 400
        
    result, status = AuthService.login_by_phone(phone, code)
    return jsonify(result), status

@auth_bp.route('/recover', methods=['POST'])
@limiter.limit("3 per hour")
def recover():
    data = request.get_json() or {}
    email = data.get('email')
    phone = data.get('phone')
    if not email and not phone:
        return jsonify({"error": "Validation Error", "message": "Введите Email или телефон"}), 400
    result, status = AuthService.send_recovery_code(email, phone)
    return jsonify(result), status

@auth_bp.route('/recover/confirm', methods=['POST'])
@limiter.limit("5 per minute")
def recover_confirm():
    data = request.get_json() or {}
    new_password = str(data.get('new_password', ''))
    
    is_strong, error_msg = validate_password_strength(new_password)
    if not is_strong:
        return jsonify({"error": "Validation Error", "message": error_msg}), 400

    result, status = AuthService.confirm_recovery(data)
    return jsonify(result), status

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    token_blocklist.add(jti)
    return jsonify({"message": "Вы вышли из системы"}), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    result, status = AuthService.refresh_token(identity)
    return jsonify(result), status

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    identity = get_jwt_identity()
    result, status = AuthService.get_current_user(identity)
    return jsonify(result), status