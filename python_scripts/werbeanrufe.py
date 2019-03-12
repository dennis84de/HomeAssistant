#!/usr/bin/python

import sys
import json 
from requests import post

def main():      
    url = 'http://192.168.2.70:8123/api/states/binary_sensor.werbeanruf'
    header = {'content-type': 'application/json'}
    payload = {'state': 'off', 'attributes': {'friendly_name': 'Werbeanruf'}}

    if len(sys.argv) == 1:   
        post(url, headers=header, data=json.dumps(payload))     
        return

    number = sys.argv[1]

    database = '/home/homeassistant/.homeassistant/www/werbeanrufe/liste.json'
    data = json.loads(open(database).read())

    for i in data:
        if i['Nummer'] == number:
            varName = i['Anrufname']
            varNummer = i['Nummer']
            varTyp = i['Anruftyp']
            varScore = i['Score']   

            payload = {'state': 'on', 'attributes': {'friendly_name': 'Werbeanruf', 'name': varName, 'number': varNummer, 'type': varTyp, 'score': varScore}}        
            break   
    
    post(url, headers=header, data=json.dumps(payload))

if __name__ == '__main__':
    main()