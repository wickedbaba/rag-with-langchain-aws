
import os
from lib.support import dynamo_support
from lib.common.dynamo_tables import config_service

def init():
    print("Initializing env variables")
    os.environ["DYNAMODB_REGION"] = "us-west-2"
    response = dynamo_support.get_item(config_service, {"service_name": "vision-service"})
    for variable in response['env_variables']:
        os.environ[variable] = response['env_variables'][variable]

init()
