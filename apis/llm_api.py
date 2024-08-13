
from flask import Blueprint, request, jsonify
from lib.support import llm_support

llm_api = Blueprint('llm_api', __name__)

@llm_api.route('/v1/llm_api/session/initiate', methods=['POST'])
def start_session():
    payload = request.get_json()
    try:
        response = llm_support.initiate_session(payload)
        return jsonify({"response": response}), 200
    except Exception as err:
        return jsonify({"response": str(err)}), 500

@llm_api.route('/v1/llm_api/chat', methods=['POST'])
def execute_llm():
    payload = request.get_json()
    try:
        response = llm_support.execute(payload)
        return jsonify({"response": response}), 200
    except Exception as err:
        return jsonify({"response": str(err)}), 500
