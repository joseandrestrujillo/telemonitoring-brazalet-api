import json
import boto3
from decimal import Decimal

def ordenar_por_timestamp(arr):
    return sorted(arr, key=lambda x: x['timestamp'], reverse=True)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Horario')
    response = table.scan()
    
    
    patients = response['Items']
    
    for patient in patients:
        for key in patient:
            if isinstance(patient[key], Decimal):
                patient[key] = str(patient[key])
    
    patients = ordenar_por_timestamp(patients)
    return {
        'statusCode': 200,
        'body': json.dumps({'alarms': patients})
    }