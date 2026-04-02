from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.roadmap_service import RoadmapService
from app import limiter

roadmap_bp = Blueprint('roadmap', __name__)

@roadmap_bp.route('/', methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_roadmap():
    user_id = get_jwt_identity()
    result, status = RoadmapService.get_roadmap(user_id)
    return jsonify(result), status

@roadmap_bp.route('/generate', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def generate_roadmap():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    level = data.get('level') 
    
    result, status = RoadmapService.generate_roadmap(user_id, level)
    return jsonify(result), status

@roadmap_bp.route('/weeks/<int:week_id>', methods=['GET'])
@jwt_required()
def get_week(week_id):
    user_id = get_jwt_identity()
    result, status = RoadmapService.get_week_detail(user_id, week_id)
    return jsonify(result), status

@roadmap_bp.route('/weeks/<int:week_id>/complete', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def complete_week(week_id):
    user_id = get_jwt_identity()
    result, status = RoadmapService.complete_week(user_id, week_id)
    return jsonify(result), status

@roadmap_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def complete_task(task_id):
    user_id = get_jwt_identity()
    result, status = RoadmapService.complete_daily_task(user_id, task_id)
    return jsonify(result), status

@roadmap_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = get_jwt_identity()
    result, status = RoadmapService.get_progress(user_id)
    return jsonify(result), status