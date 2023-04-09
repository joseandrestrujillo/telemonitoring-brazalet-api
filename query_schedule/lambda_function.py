import json
import boto3
from datetime import datetime
from decimal import Decimal



client = boto3.client('iot-data', region_name='eu-west-3')
dynamodb = boto3.resource('dynamodb')


def seconds_until_timestamp(current_timestamp, items):
    result = []
    for item in items:
        timestamp = int(item['timestamp'])
        seconds_until = timestamp - current_timestamp
        result.append(seconds_until)
    return result

def lambda_handler(event, context):
    table = dynamodb.Table('Horario')
    current_timestamp = int(datetime.now().timestamp())
    
    response = table.scan(
        FilterExpression='#ts > :ts and device_id = :device_id',
        ExpressionAttributeNames={
            '#ts': 'timestamp'
        },
        ExpressionAttributeValues={
            ':ts': current_timestamp,
            ':device_id': 'adafruitlora'
        }
    )
    
    # Mostrar los resultados
    items = seconds_until_timestamp(current_timestamp, response['Items'])
    response = client.publish(
        topic='lorawan/downlink',
        qos=0,
        payload=json.dumps({
          "thingName": "70B3D57ED005C19E",
          "payload": {
            "items": items
          }
        })
    )
