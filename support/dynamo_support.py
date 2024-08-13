
import os
import boto3

service_name = 'dynamodb'

def get_resource():
    resource = boto3.resource(service_name=service_name, region_name=os.environ["DYNAMODB_REGION"])
    return resource

def get_client():
    client = boto3.client(service_name=service_name, region_name=os.environ["DYNAMODB_REGION"])
    return client

def get_item(table_name, key):
    try:
        table = get_resource().Table(table_name)
        return table.get_item(Key=key, ConsistentRead=True)['Item']
    except Exception as err:
        print(err)

def insert_item(table_name, item):
    try:
        table = get_resource().Table(table_name)
        table.put_item(
            Item=item
        )
        return True
    except Exception as err:
        print(err)

def scan_item_with_filter(table_name, filter_expr):
    table = get_resource().Table(table_name)
    result = table.scan(
        FilterExpression=filter_expr,
        ConsistentRead=True
    )
    data = result["Items"]
    while 'LastEvaluatedKey' in result:
        result = table.scan(FilterExpression=filter_expr,
                            ConsistentRead=True,
                            ExclusiveStartKey=result['LastEvaluatedKey']
                            )
        data.extend(result['Items'])
    return data
