import json
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Pacientes')
    response = table.scan()
    
    patients = response['Items']
    
    for patient in patients:
        patient["criteria_events"]["events"] = list(patient["criteria_events"]["events"]) 
    
    
    return {
        'statusCode': 200,
        'body': json.dumps({'patients': patients})
    }