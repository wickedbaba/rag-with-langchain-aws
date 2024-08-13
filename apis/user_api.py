
from flask import Blueprint, request, jsonify
from lib.support import user_support

user_api = Blueprint('user_api', __name__)

@user_api.route('/v1/user/create', methods=['POST'])
def create_user():
    payload = request.get_json()
    try:
        user = user_support.create_user(payload)
        return jsonify({"response": user}), 200
    except Exception as err:
        return jsonify({"response": str(err)}), 500

@user_api.route('/v1/user/validate', methods=['POST'])
def validate_user():
    payload = request.get_json()
    try:
        user_support.validate_user(payload)
        return jsonify({"response": True}), 200
    except Exception as err:
        return jsonify({"response": str(err)}), 403
