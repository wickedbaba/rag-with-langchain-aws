
import uuid
from lib.common.dynamo_tables import users
from lib.support import dynamo_support


def create_user(payload):
    user = {
        "user_id": str(uuid.uuid4()),
        "name": payload['name'],
        "email": payload['email'],
        "password": payload['password'],
        "repos": []
    }
    dynamo_support.insert_item(users, user)
    return user

def add_user_repos(email, repo_id):
    user = dynamo_support.get_item(users, {"email": email})
    if not user:
        raise Exception("User does not exists")
    if repo_id not in user['repos']:
        user["repos"].append(repo_id)
    dynamo_support.insert_item(users, user)
    return user

def delete_user_repos(email, repo_id):
    user = dynamo_support.get_item(users, {"email": email})
    if not user:
        raise Exception("User does not exists")
    if repo_id in user['repos']:
        user["repos"].remove(repo_id)
    user = dynamo_support.insert_item(users, user)
    return user

def get_user(email):
    user = dynamo_support.get_item(users, {"email": email})
    if not user:
        raise Exception("User does not exists")
    return user

def validate_user(payload):
    user = get_user(payload['email'])
    if user['password'] != payload['password']:
        raise Exception("Invalid password")
