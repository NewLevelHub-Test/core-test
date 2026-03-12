from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService
from app.utils.rate_limit import rate_limit, sms_rate_limit

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    result, status = AuthService.register(data)
    return jsonify(result), status


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result, status = AuthService.login(data)
    return jsonify(result), status


@auth_bp.route('/send-code', methods=['POST'])
@sms_rate_limit
def send_code():
    data = request.get_json()
    result, status = AuthService.send_sms_code(data.get('phone'))
    return jsonify(result), status


@auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    result, status = AuthService.verify_sms_code(data.get('phone'), data.get('code'))
    return jsonify(result), status


@auth_bp.route('/login-phone', methods=['POST'])
def login_phone():
    data = request.get_json()
    result, status = AuthService.login_by_phone(data.get('phone'), data.get('code'))
    return jsonify(result), status


@auth_bp.route('/recover', methods=['POST'])
@sms_rate_limit
def recover():
    data = request.get_json()
    result, status = AuthService.send_recovery_code(data.get('email'), data.get('phone'))
    return jsonify(result), status


@auth_bp.route('/recover/confirm', methods=['POST'])
def recover_confirm():
    data = request.get_json()
    result, status = AuthService.confirm_recovery(data)
    return jsonify(result), status


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
