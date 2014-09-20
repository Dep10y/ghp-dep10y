import random
import requests
import json
import time
import os.path
import tempfile
import subprocess
from firebase import firebase, jsonutil
from copy import deepcopy
from threading import Thread

TOKEN = '91a4cf30bfdaae8a3fa2a54d55fe7cfa79ce882bed94bff73f7db8c584c27817'
def doGet(path, args={}):
    resp = json.loads(requests.get('https://api.digitalocean.com/v2%s' % path, params=args, headers={'Authorization':'Bearer %s' % TOKEN}).text)
    return resp

def doDelete(path):
    resp = requests.delete('https://api.digitalocean.com/v2%s' % path, headers={'Authorization':'Bearer %s' % TOKEN}).text
    return True

def doPost(path, args={}):
    resp = json.loads(requests.post('https://api.digitalocean.com/v2%s' % path, data=json.dumps(args), headers={'Authorization':'Bearer %s' % TOKEN, 'Content-Type':'application/json'}).text)
    return resp

def doDeploy(project_id, f):
    projects = firebase.get('/projects')
    p = None
    for project in projects:
        if project_id in projects[project]:
            p = projects[project][project_id]
    if not p:
        print("p doesn't exist")
        return False

    if 'droplet_id' not in p:
        print("No droplet id")
        return False

    droplet = doGet('/droplets/%s' % p['droplet_id'])['droplet']
    files = f
    with tempfile.mkdtemp() as tmpdir:
        for f in files:
            fi = open(os.path.join(tmpdir, f['filepath']), 'w')
            fi.write(f['text'])
            fi.close()
        p = subprocess.Popen(['/usr/bin/rsync', '-az', tmpdir, 'web@%s:web' % droplet['name']])
        print p.wait()
        print('rsync done!')
    if p['type'] == 'flask':
        p = subprocess.Popen(['/usr/bin/ssh', '-t', 'web@%s' % droplet['name'], '"kill `cat ~/.app_pid`; sleep 3; kill -9 `cat ~/.app_pid`; "'])
        print p.wait()
        p = subprocess.Popen('/usr/bin/ssh -t web@%s "screen \"python web/app.py\" &; echo $! > ~/.app_pid;"' % droplet['name'], shell=True)
        print p.wait()
    else:
        print('Unsupported type!')
        return False

if __name__ == '__main__':
    firebase = firebase.FirebaseApplication('https://dep10y.firebaseio.com', authentication=None)
    while True:
        deploys = firebase.get('/files')
        if deploys:
            for i in deploys:
                val = deploys[i]
                firebase.delete('/files/%s' % i)
                thread = Thread(target=doDeploy, args=(i, val))
                thread.start()
        time.sleep(3)