import os
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
import boto3
import json

ses_client = boto3.client('ses')
from_email = "avisos.teleseguimiento@gmail.com"

available_status = {
  'Sigo correctamente el tratamiento.': "evento1",
  'Ha fallado el plan previsto. No tengo la protección esperable por mi entorno. No sigo el tratamiento.': "evento2",
  'Siento otra vez el miedo y algo va a pasar.': "evento3",
  'Estoy en una situación peligrosa para mi o mi entorno y necesito ayuda.': "evento4"
}

def lambda_handler(event, context):
    
    timerange_alarm = True
    if event['patient']['criteria_timerange']['M']['active']['BOOL']:
        timestamp = int(event['event_reported']['timestamp']['N'])
        since = event['patient']['criteria_timerange']['M']['since']['S']
        until = event['patient']['criteria_timerange']['M']['until']['S']
        timerange_alarm = is_in_range(timestamp, until, since)
    
    
    event_alarm = False
    if event['patient']['criteria_events']['M']['active']['BOOL']:
        events_of_criteria = valores = [d.get('S') for d in event['patient']['criteria_events']['M']['events']['L']]
        if available_status[event['event_reported']['reported_status']['S']] in events_of_criteria:
            event_alarm = True
        else:
            event_alarm = False
            
            
    localization_alarm = True
    if event['patient']['criteria_localization']:
        if is_dangerous(event['event_reported']['localization_data']['M']['lat'],event['event_reported']['localization_data']['M']['long']):
            localization_alarm = True
        else:
            localization_alarm = False
    
    

    if timerange_alarm and event_alarm and localization_alarm:
        print("Enviando email...")
        body_html = generate_html(event['event_reported'], event['patient'])
        email=event['patient']['notification_email']['S']
        send_email(body_html, email)
    else:
        print("No se envia email.")

def is_dangerous(lat, lon):
    result = find_nearby_features(lat, lon, 50)
    if ((len(result['bridges']) == 0)and (len(result['rivers']) == 0)and (len(result['highways']) == 0)and (len(result['railway']) == 0)):
        return True
    else:
        return False
    
def is_in_range(timestamp_unix, until_str, since_str):
    timestamp = datetime.fromtimestamp(timestamp_unix)
    until = datetime.strptime(until_str, '%H:%M')
    since = datetime.strptime(since_str, '%H:%M')

    hour = timestamp.hour

    if until < since:
        until += timedelta(days=1)

    until_today = datetime.combine(timestamp.date(), until.time())
    since_today = datetime.combine(timestamp.date(), since.time())

    if until_today < since_today:
        until_today += timedelta(days=1)

    if since_today.hour <= hour or hour <= until_today.hour:
        return True
    else:
        return False

def find_nearby_features(latitude, longitude, radius=500):
    overpass_url = "https://overpass-api.de/api/interpreter"

    overpass_query = f"""
    [out:json];
    (
      way["bridge"="yes"](around:{radius},{latitude},{longitude});
      way["bridge"="viaduct"](around:{radius},{latitude},{longitude});
      way["waterway"="river"](around:{radius},{latitude},{longitude});
      way["highway"="motorway"](around:{radius},{latitude},{longitude});
      way["railway"](around:{radius},{latitude},{longitude});
    );
    out body;
    >;
    out skel qt;
    """
    response = requests_get(overpass_url, params={'data': overpass_query})
    data = json.loads(response)

    found_features = {
        'bridges': [],
        'rivers': [],
        'highways': [],
        'railway': []
    }

    for element in data['elements']:
        if element['type'] == 'way':
            tags = element.get('tags', {})
            if 'bridge' in tags:
                found_features['bridges'].append(element)
            elif tags.get('waterway') == 'river':
                found_features['rivers'].append(element)
            elif 'highway' in tags:
                found_features['highways'].append(element)
            elif 'railway' in tags:
                found_features['railway'].append(element)

    return found_features

def requests_get(url, params=None, headers=None, timeout=None):
    url =url + '?' + urlencode(params)
    """ if params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
    """
    req = Request(url)
    if headers:
        for header, value in headers.items():
            req.add_header(header, value)

    try:
        response = urlopen(req, timeout=timeout)
    except HTTPError as e:
        raise Exception(f'Request failed with status {e.code}: {e.reason}')

    return response.read().decode('utf-8')

def generate_html(event, patient):
    time_text = ""
    if patient['criteria_timerange']['M']['active']['BOOL']:
        timestamp = datetime.fromtimestamp(int(event['timestamp']['N']))
        hora = timestamp.strftime('%I')
        minutos = timestamp.strftime('%M')
        am_pm = timestamp.strftime('%p')
        time_text = f""", a las {hora}:{minutos} {am_pm} del día {timestamp.strftime('%d/%m/%Y')},"""
    
    loc_text = ""
    if patient['criteria_localization']:
        loc_text = "cerca de lugares potencialmente peligrosos (puentes, autovias, vias de tren, rios)"
    

    return f"""<html>
        <head></head>
        <body>
            <h2>Alerta con el paciente: {patient['nombre']['S']} {patient['apellidos']['S']}</h2>
            <br/>
            <p>
                Este correo ha sido enviado ya que {patient['nombre']['S']} {patient['apellidos']['S']} ha enviado{time_text} el evento: "{event['reported_status']['S']}" {loc_text}.
            </p>
            <a href="https://main.d34uccelyjlg2i.amplifyapp.com/portal/events" target="_blank">Consulte el historial de eventos del paciente</a>
        </body>
        </html>
    """

def send_email(body_html, email):
    email_message = {
        'Body': {
            'Html': {
                'Charset': 'utf-8',
                'Data': body_html,
            },
        },
        'Subject': {
            'Charset': 'utf-8',
            'Data': "Hello from AWS SES",
        },
    }
    try:
        ses_response = ses_client.send_email(
            Destination={
                'ToAddresses': [email],
            },
            Message=email_message,
            Source=from_email,
        )
    except:
        ses_client.verify_email_identity(
            EmailAddress=email
        )