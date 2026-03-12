from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.analysis_service import AnalysisService

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/game/<int:game_id>', methods=['GET'])
@jwt_required()
def analyze_game(game_id):
    user_id = get_jwt_identity()
    result, status = AnalysisService.analyze_game(user_id, game_id)
    return jsonify(result), status


@analysis_bp.route('/position', methods=['POST'])
@jwt_required()
def analyze_position():
    data = request.get_json()
    result, status = AnalysisService.analyze_position(data.get('fen'))
    return jsonify(result), status


@analysis_bp.route('/mistakes', methods=['GET'])
@jwt_required()
def get_mistakes():
    user_id = get_jwt_identity()
    result, status = AnalysisService.get_user_mistakes(user_id)
    return jsonify(result), status


@analysis_bp.route('/mistakes/<int:mistake_id>/exercises', methods=['GET'])
@jwt_required()
def get_mistake_exercises(mistake_id):
    result, status = AnalysisService.get_exercises_for_mistake(mistake_id)
    return jsonify(result), status
