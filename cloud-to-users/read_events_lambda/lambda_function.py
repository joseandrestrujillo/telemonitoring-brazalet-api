import json
import boto3
from decimal import Decimal
    
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Eventos')
    response = table.scan()
    
    items = response['Items']
    
    # Convertir los valores de tipo Decimal a cadenas de caracteres (para la latitud y longitud)
    for item in items:
        for key in item:
            if isinstance(item[key], Decimal):
                item[key] = str(item[key])
    
    return {
        'statusCode': 200,
        'body': json.dumps({'items': items})
    }
