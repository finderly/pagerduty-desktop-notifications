#!/usr/bin/env python
# 
# ga@shpock.com -- inspired by John McFarlane's script
# 

import json
import logging
import time
import pynotify
import requests

log = logging.getLogger('pagerduty')
token = ''
user_name = ''

api = 'https://finderly.pagerduty.com/api/v1/'
headers = {'Content-type': 'application/json',
           'Authorization': 'Token token=%s' % token}

pynotify.init('Pagerduty issue applet')

# get user id from user name
def getUserId(name):
    endpoint = 'https://finderly.pagerduty.com/api/v1/' + 'users'
    query = {'query': name}
    r = requests.get(endpoint, params=query, headers=headers)
    r.raise_for_status()
    r_list = r.json()
    user_id = r_list['users'][0]['id']
    
    return user_id

# poll pd api for incidents
def poll(userid):
    endpoint = 'https://finderly.pagerduty.com/api/v1/' + 'incidents'
    params = {'assigned_to': userid,
          'sort_by': 'urgency:asc,incident_number:desc',
          'status': 'triggered'}
    r = requests.get(endpoint, params=params, headers=headers)
    r.raise_for_status()
    for incident in r.json().get('incidents', []):
        show(userid, incident)
    else:
        log.info('No assigned issues')

# show notification on screen
def show(userid, incident):
    body_int = json.loads(json.dumps(incident))
    user = body_int['assigned_to_user']['id']

    if user == userid:
        summary = 'PagerDuty: ' + body_int['urgency']
        if 'description' in body_int:
            body = body_int['trigger_summary_data']['description']
        else:
            body = body_int['trigger_summary_data']['subject']
        msg = pynotify.Notification(summary, body)
        msg.set_urgency(pynotify.URGENCY_NORMAL)
        if not msg.show():
            print 'failed to show notification'


def main():
    fmt = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    noisy = logging.getLogger('urllib3.connectionpool')
    noisy.setLevel(logging.WARNING)
    user_id = getUserId(user_name)

    while True:
        try:
            poll(user_id)
        except Exception:
            log.exception('Something went wrong.')
        finally:
            time.sleep(60)

if __name__ == '__main__':
    main()
