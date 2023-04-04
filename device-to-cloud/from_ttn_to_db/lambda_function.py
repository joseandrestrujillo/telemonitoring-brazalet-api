import json
import boto3
import uuid

client = boto3.client('dynamodb')

print('Loading function ')

available_status = [
  'Ha fallado el plan previsto. No tengo la protección esperable por mi entorno.',
  'Algo ha fallado con el tratamiento: no lo he conseguido, algún efecto secundario inesperado, no lo estoy tomando.',
  'Siento otra vez el miedo y algo va a pasar.',
  'Tengo ganas de morir.'
]

def lambda_handler(event, context):
    ueid = str(uuid.uuid1())
    timestamp = str(event['timestamp'])
    
    data = client.put_item(
        TableName='Eventos',
        Item={
          "ueid": {
            "S": ueid
          },
          "timestamp": {
            "N": timestamp
          },
          "reported_status": {
            "S": available_status[event['reported_status']]
          },
          "localization_data": {
            "M": {
              "lat": {
                "S": event['localization_data'][0]
              },
              "long": {
                "S": event['localization_data'][1]
              }
            }
          }
        }
    )