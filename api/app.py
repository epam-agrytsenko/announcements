import os
import json
import logging
import boto3
from uuid import uuid4
from datetime import datetime as dt


REGION = os.environ['AWS_REGION']
LOG_LEVEL = os.environ['LOG_LEVEL']
ANNOUNCEMENT_TABLE_NAME = os.environ['ANNOUNCEMENT_TABLE_NAME']


log = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


class Database:

    def __init__(self):
        session = boto3.Session(region_name=REGION)
        resource = session.resource('dynamodb')
        self.table = resource.Table(ANNOUNCEMENT_TABLE_NAME)

    def put_item(self, item):
        return self.table.put_item(Item=item)

    def get_item(self, key):
        resp = self.table.get_item(Key=key)
        return resp.get('Item', None)

    def list_items(self):
        resp = self.table.scan()
        res = resp['Items']
        while 'LastEvaluatedKey' in resp:
            resp = self.table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
            res.extend(resp['Items'])
        return res

    def delete_item(self, key):
        return self.table.delete_item(Key=key)


def validate_fields(request):
    if 'title' not in request:
        raise ValidationError("missing 'title'")
    if 'description' not in request:
        raise ValidationError("missing 'description'")
    return True


def response(code, body):
    body = json.dumps(body)
    params = {
        'statusCode': code,
        'body': body,
        'headers': {'content': 'application/json'},
    }
    return params


def error(code, message=''):
    params = {
        'statusCode': code,
        'body': {'error': message},
        'headers': {'content': 'application/json'},
    }
    return params


def create_announcement(event, context):

    try:
        body = json.loads(event['body'])
    except (ValueError, TypeError) as e:
        log.error(str(e))
        return error(400, 'Request is missing or is not json serializable')
    try:
        validate_fields(body)
    except ValidationError as e:
        log.error(str(e), exc_info=1)
        return error(400, str(e))
    date_str = body.get('date', None)
    if date_str is None:
        creation_date = dt.now().isoformat()
    else:
        creation_date = dt.strptime(date_str, '%a, %d %b %Y %H:%M:%S').isoformat()
    item = {
        'id': f"{uuid4().hex}",
        'title': body['title'],
        'date': creation_date,
        'description': body['description']
    }
    db = Database()
    db.put_item(item)
    return response(201, item)


def list_announcements(event, context):
    db = Database()
    items = db.list_items()
    return response(200, items)


