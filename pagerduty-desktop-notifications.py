#!/usr/bin/env python
# 
# ga@shpock.com -- inspired by John McFarlane's script
# 

import json
import logging
import time
import os
import pynotify
import requests

# set diplay to be used
os.environ.setdefault('XAUTHORITY', '~/.Xauthority')
os.environ.setdefault('DISPLAY', ':0.0')

log = logging.getLogger('pagerduty')
token = ''
user_name = ''

api = 'https://api.pagerduty.com/'
headers = {'Accept': 'application/vnd.pagerduty+json;version=2',
           'Content-type': 'application/json',
           'Authorization': 'Token token=%s' % token}

pynotify.init('Pagerduty issue applet')

# get user id from user name
def getUserId(name):
    endpoint = api + 'users'
    query = {'query': name}
    r = requests.get(endpoint, params=query, headers=headers)
    r.raise_for_status()
    r_list = r.json()
    user_id = r_list['users'][0]['id']
    
    return user_id

# poll pd api for incidents
def poll(userid):
    endpoint = 'https://api.pagerduty.com/' + 'incidents'
    params = {'include[]': 'assignees',
          'sort_by': 'urgency:asc,incident_number:desc',
          'statuses[]': 'triggered'}
    r = requests.get(endpoint, params=params, headers=headers)
    r.raise_for_status()
    for incident in r.json().get('incidents', []):
        show(userid, incident)
    else:
        log.info('No assigned issues')

# show notification on screen
def show(userid, incident):
    body_int = json.loads(json.dumps(incident))
    user = body_int['assignments'][0]['assignee']['id']

    if user == userid:
        summary = 'PagerDuty: ' + body_int['urgency']
       # if 'description' in body_int['trigger_summary_data']:
       #     body = body_int['trigger_summary_data']['description']
       # else:
       #     body = body_int['trigger_summary_data']['subject']
        body = body_int['summary']
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
