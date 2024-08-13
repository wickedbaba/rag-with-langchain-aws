
from flask import Blueprint, request, jsonify
from lib.support import git_repo_support

git_repo_api = Blueprint('git_repo_api', __name__)

@git_repo_api.route('/v1/repo/add', methods=['POST'])
def export_repo():
    payload = request.get_json()
    try:
        repo_id = git_repo_support.add_repo(payload)
        return jsonify({"response": repo_id}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@git_repo_api.route('/v1/repo/delete', methods=['POST'])
def delete_repo():
    payload = request.get_json()
    try:
        git_repo_support.delete_repo(payload)
        return jsonify({"response": True}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@git_repo_api.route('/v1/repo/sync', methods=['POST'])
def sync_repo():
    payload = request.get_json()
    try:
        git_repo_support.sync_repo(payload)
        return jsonify({"response": True}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@git_repo_api.route('/v1/repo/fetch', methods=['POST'])
def fetch_repos():
    payload = request.get_json()
    try:
        repos = git_repo_support.fetch_repos_by_user(payload['email'])
        return jsonify({"response": repos}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
