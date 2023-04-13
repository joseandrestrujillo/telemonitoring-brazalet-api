import json
from urllib.parse import parse_qs
import boto3

client = boto3.client('dynamodb')
ses_client = boto3.client('ses')

def format_patient(body):
    attributes = parse_qs(body)
    print(body)
    print(attributes)
    patient = {
        "dni": {
            "S": attributes["dni"][0]
        },
        "nombre": {
            "S": attributes["nombre"][0]
        },
        "apellidos": {
            "S": attributes["apellidos"][0]
        },
        "fecha_nacimiento": {
            "S": attributes["fecha_nacimiento"][0]
        },
        "telefono": {
            "S": attributes["telefono"][0]
        },
        "notification_email": {
            "S": attributes["email"][0]
        },
        "criteria_events": {
            "M": {
                "active": {
                    "BOOL": True if attributes.get("eventos1", ["off"])[0] == "on" else False
                },
                "events": {
                    "L": []
                }
            }
        },
        "criteria_timerange": {
            "M": {
                "active": {
                    "BOOL": True if attributes.get("horario1", ["off"])[0] == "on" else False
                },
                "since": {
                    "S": ""
                },
                "until": {
                    "S": ""
                }
            }
        },
        "criteria_localization": {
            "BOOL": True if attributes.get("lugar1", ["off"])[0] == "on" else False
        }
        
    }
    
    if attributes.get("eventos1", ["off"])[0] == "on":
        for event in attributes["opciones1"]:
            patient["criteria_events"]["M"]["events"]["L"].append({
                "S": event
            })
    
    if attributes.get("horario1", ["off"])[0] == "on":
        patient["criteria_timerange"]["M"]["since"]["S"] = attributes["hora_desde1"][0]
    if attributes.get("horario1", ["off"])[0] == "on":
        patient["criteria_timerange"]["M"]["until"]["S"] = attributes["hora_hasta1"][0]
    return patient

def lambda_handler(event, context):
    try:
        ses_client.verify_email_identity(
            EmailAddress=event["body"]["email"]
        )
    except:
        print("")
    patient = format_patient(event["body"])
    print(patient)
    data = client.put_item(
        TableName='Pacientes',
        Item=patient
    )
    return {
        "headers": {"Location": "https://main.d34uccelyjlg2i.amplifyapp.com/", },
        "statusCode": 301,
    }
