
from flask import Blueprint, request, jsonify
from lib.support import s3_support

s3_read_api = Blueprint('s3_read_api', __name__)

@s3_read_api.route('/v1/s3/read', methods=['POST'])
def read_s3():
    payload = request.get_json()
    response = s3_support.read_json_from_s3(payload['bucket'], payload['key'])
    return jsonify({"response": response}), 200
