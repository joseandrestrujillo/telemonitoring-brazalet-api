import json
import boto3
from decimal import Decimal
    
def ordenar_por_timestamp(arr):
    return sorted(arr, key=lambda x: x['timestamp'], reverse=True)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Eventos')
    response = table.scan()
    
    items = response['Items']
    
    # Convertir los valores de tipo Decimal a cadenas de caracteres (para la latitud y longitud)
    for item in items:
        for key in item:
            if isinstance(item[key], Decimal):
                item[key] = int(item[key])
    
    
    items = ordenar_por_timestamp(items)
    return {
        'statusCode': 200,
        'body': json.dumps({'items': items})
    }
