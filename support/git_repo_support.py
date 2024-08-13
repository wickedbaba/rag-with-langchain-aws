import json
import os
import shutil
import uuid
import git
from lib.support import s3_support, dynamo_support, user_support
from lib.common.dynamo_tables import repos
from boto3.dynamodb.conditions import Attr

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_up(directories=[], files=[]):
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed directory {directory}")

    for file_name in files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed file {file_name}")

def clone_repo(gitlab_url, branch, repo_dir):
    ensure_directory_exists(repo_dir)
    clone_url = gitlab_url.replace('https://', f"https://{os.environ['GIT_USER']}:{os.environ['GIT_TOKEN']}@")
    print(f"Cloning repository from {gitlab_url} (branch: {branch})")
    git.Repo.clone_from(clone_url, repo_dir, branch=branch)
    print("Repository cloned successfully.")

def collect_files_content(repo_dir):
    files_data = {}
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                relative_path = os.path.relpath(file_path, repo_dir)
                files_data[relative_path] = f.read()
    return files_data

def export_repo(payload):
    clone_repo(payload['gitlab_url'], payload['branch'], payload['repo_name'])
    files_data = collect_files_content(payload['repo_name'])
    s3_support.write_json_to_s3(files_data, os.environ['REPO_EXPORT_BUCKET'], payload['s3_file_name'])
    clean_up([payload['repo_name']])
    print("Operation completed.")

def get_repo_content_from_s3(repo_name, branch):
    existing_repo = get_repo(repo_name, branch)
    json_data = s3_support.read_json_from_s3(os.environ['REPO_EXPORT_BUCKET'], existing_repo['s3_file_name'])
    return json_data

def fetch_repos_by_user(user_email):
    user = user_support.get_user(user_email)
    if user['repos']:
        return dynamo_support.scan_item_with_filter(repos, Attr('repo_id').is_in(user['repos']))
    return []

def get_repo(repo_name, branch):
    key = {
        "repo_name": repo_name,
        "branch": branch
    }
    response = dynamo_support.get_item(repos, key)
    return response

def sync_repo(payload):
    existing_repo = get_repo(payload['repo_name'], payload['branch'])
    export_repo(existing_repo)

def add_repo(payload):
    payload['repo_name'] = payload['gitlab_url'].split('/')[-1].split('.git')[0]
    existing_repo = get_repo(payload['repo_name'], payload['branch'])
    if existing_repo:
        payload.update(existing_repo)
        repo_id = existing_repo['repo_id']
    else:
        new_repo = {
            "repo_id": str(uuid.uuid4()),
            "gitlab_url": payload['gitlab_url'],
            "repo_name": payload['repo_name'],
            "branch": payload['branch'],
            "s3_file_name": "repository_data/" + payload['gitlab_url'].replace('https://gitlab.com/', '').replace('.git', f"_{payload['branch']}.json")
        }
        dynamo_support.insert_item(repos, new_repo)
        payload.update(new_repo)
        repo_id = new_repo['repo_id']
    user_support.add_user_repos(payload['email'], repo_id)
    export_repo(payload)
    return repo_id

def delete_repo(payload):
    return user_support.delete_user_repos(payload['email'], payload['repo_id'])
