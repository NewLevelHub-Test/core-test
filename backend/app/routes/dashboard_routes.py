from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = get_jwt_identity()
    result, status = DashboardService.get_dashboard(user_id)
    return jsonify(result), status


@dashboard_bp.route('/recommendation', methods=['GET'])
@jwt_required()
def get_recommendation():
    user_id = get_jwt_identity()
    result, status = DashboardService.get_recommendation(user_id)
    return jsonify(result), status


@dashboard_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity():
    user_id = get_jwt_identity()
    result, status = DashboardService.get_activity(user_id)
    return jsonify(result), status
