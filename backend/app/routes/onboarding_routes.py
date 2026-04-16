from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.onboarding_service import OnboardingService
from app import limiter

onboarding_bp = Blueprint('onboarding', __name__)


@onboarding_bp.route('/test', methods=['GET'])
@jwt_required()
def get_placement_test():
    result, status = OnboardingService.get_test()
    return jsonify(result), status


@onboarding_bp.route('/test/submit', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def submit_placement_test():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    answers = data.get('answers', [])
    if not isinstance(answers, list) or len(answers) != 10:
        return jsonify({"error": "Нужно ответить на все 10 вопросов"}), 400
    result, status = OnboardingService.submit_test(user_id, answers)
    return jsonify(result), status


@onboarding_bp.route('/game/start', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def start_placement_game():
    user_id = get_jwt_identity()
    result, status = OnboardingService.start_placement_game(user_id)
    return jsonify(result), status


@onboarding_bp.route('/complete', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def complete_onboarding():
    user_id = get_jwt_identity()
    result, status = OnboardingService.complete_onboarding(user_id)
    return jsonify(result), status
