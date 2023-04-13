import json
from datetime import datetime
from urllib.parse import parse_qs
import boto3
import uuid

client = boto3.client('dynamodb')

def parse_dates(query_string):
    qs_dict = parse_qs(query_string)
    dates_dict = []
    for key, value in qs_dict.items():
        if key.startswith('date-'):
            date_obj = datetime.fromisoformat(value[0])
            dates_dict.append(str(date_obj.timestamp()))
    return dates_dict



def lambda_handler(event, context):
    timestamps = parse_dates(event["body"])
    for timestamp in timestamps:
        uhid = str(uuid.uuid1())
        data = client.put_item(
            TableName='Horario',
            Item={
              "uhid": {
                "S": uhid
              },
              "device_id": {
                "S": "adafruitlora"
              },
              "timestamp": {
                "N": timestamp
              },
              "sync_status": {
                "S": "En espera de sincronización"
              },
              
            }
        )
    return {
        "headers": {"Location": "https://main.d34uccelyjlg2i.amplifyapp.com/alarms/", },
        "statusCode": 301,
    }
