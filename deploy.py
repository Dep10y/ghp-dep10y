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

def doDeploy(project_id, fals):
    projects = firebase.get('/projects', name=None, params=None)
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
    files = fals
    tmpdir = tempfile.mkdtemp()
    for f in files:
        fi = open(os.path.join(tmpdir, files[f]['filepath']), 'w')
        fi.write(files[f]['text'])
        fi.close()
    po = subprocess.Popen('/usr/bin/rsync -aze "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --delete %s/ web@%s:web' % (tmpdir, droplet['name']), shell=True)
    print po.wait()
    print('rsync done!')
    if p['type'] == 'flask':
        po = subprocess.Popen("/usr/bin/ssh %s -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -l web 'kill `cat /home/web/.app_pid`; sleep 3; kill -9 `cat /home/web/.app_pid`; '" % droplet['name'], shell=True)
        print po.wait()
        po = subprocess.Popen('/usr/bin/ssh %s -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -l web \'screen -m -d /usr/bin/python /home/web/web/app.py; echo `pidof SCREEN` > /home/web/.app_pid\'' % droplet['name'], shell=True)
        print po.wait()
    elif p['type'] == 'sinatra':
        po = subprocess.Popen("/usr/bin/ssh %s -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -l web 'kill `cat /home/web/.app_pid`; sleep 3; kill -9 `cat /home/web/.app_pid`; '" % droplet['name'], shell=True)
        print po.wait()
        po = subprocess.Popen('/usr/bin/ssh %s -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -l web \'screen -m -d /usr/bin/ruby /home/web/web/app.rb; echo `pidof SCREEN` > /home/web/.app_pid\'' % droplet['name'], shell=True)
        print po.wait()
    else:
        print('Unsupported type!')
        return False

if __name__ == '__main__':
    firebase = firebase.FirebaseApplication('https://dep10y.firebaseio.com', authentication=None)
    while True:
        deploys = firebase.get('/files', name=None, params=None)
        if deploys:
            for i in deploys:
                val = deploys[i]
                print(i,val)
                firebase.delete('/files', i)
                thread = Thread(target=doDeploy, args=(i, val))
                thread.start()
        time.sleep(3)
