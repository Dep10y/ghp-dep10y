import random
import requests
import json
import time
import xml.etree.ElementTree as ET
from firebase import firebase, jsonutil
from copy import deepcopy
from threading import Thread

TOKEN = '91a4cf30bfdaae8a3fa2a54d55fe7cfa79ce882bed94bff73f7db8c584c27817'
def doGet(path, args={}):
    print(args)
    resp = json.loads(requests.get('https://api.digitalocean.com/v2%s' % path, params=args, headers={'Authorization':'Bearer %s' % TOKEN}).text)
    return resp

def doDelete(path):
    resp = requests.delete('https://api.digitalocean.com/v2%s' % path, headers={'Authorization':'Bearer %s' % TOKEN}).text
    return True

def doPost(path, args={}):
    print(json.dumps(args))
    resp = json.loads(requests.post('https://api.digitalocean.com/v2%s' % path, data=json.dumps(args), headers={'Authorization':'Bearer %s' % TOKEN, 'Content-Type':'application/json'}).text)
    return resp

def doNC(args):
    print(dict({'APIUser':'vacation9','APIKey':'8ce48ef919c7436e9be8d7d1567c80dc','UserName':'Vacation9','ClientIp':'129.97.250.143'}.items()+args.items()))
    resp = requests.get('https://api.namecheap.com/xml.response', params=dict({'APIUser':'vacation9','APIKey':'8ce48ef919c7436e9be8d7d1567c80dc','UserName':'Vacation9','ClientIp':'129.97.250.143'}.items()+args.items())).text
    print resp
    return ET.fromstring(resp)

def doNCPost(args):
    print(dict({'APIUser':'vacation9','APIKey':'8ce48ef919c7436e9be8d7d1567c80dc','UserName':'Vacation9','ClientIp':'129.97.250.143'}.items()+args.items()))
    resp = requests.post('https://api.namecheap.com/xml.response', data=dict({'APIUser':'vacation9','APIKey':'8ce48ef919c7436e9be8d7d1567c80dc','UserName':'Vacation9','ClientIp':'129.97.250.143'}.items()+args.items())).text
    return ET.fromstring(resp)

def getRecords():
    domlist = doNC({'Command':'namecheap.domains.dns.getHosts','SLD':'dep10y','TLD':'me'})
    doms = list(domlist)
    print doms
    newsets = {}
    for olddom in range(len(doms[3][0])):
        pos = olddom + 2
        stuff = doms[3][0][olddom].attrib
        newsets['HostName%s' % pos] = stuff['Name']
        newsets['TTL%s' % pos] = stuff['TTL']
        newsets['RecordType%s' % pos] = stuff['Type']
        newsets['Address%s' % pos] = stuff['Address']
        if 'MXPref' in stuff:
            newsets['MXPref%s' % pos] = stuff['MXPref']
    return newsets

def newDroplet(gh_id=None, int_id=None):
    if gh_id:
        firebase.patch('/projects/%s/%s/' % (gh_id, int_id), data={'state': 'Creating droplet'})
    project = firebase.get('/projects/%s/%s' % (gh_id, int_id), name=None, params=None)
    num = random.randint(1111111,9999999)
    images = {'flask':6219398,'sinatra':6219719}
    newdrop = doPost('/droplets',
        {'name':'%s%s.dep10y.me' % (project['type'],num),
        'region':'nyc3',
        'image': images[project['type']],
        'ssh_keys':[325148],
        'size':'512mb'})
    if gh_id:
        firebase.patch('/projects/%s/%s/' % (gh_id, int_id), data={'state': 'Waiting for creation to finish', 'droplet_id':newdrop['droplet']['id']})
    time.sleep(30)
    if gh_id:
        firebase.patch('/projects/%s/%s/' % (gh_id, int_id), data={'state': 'Setting DNS'})
    createdDrop = doGet('/droplets/%s' % newdrop['droplet']['id'])
    newsets = getRecords()
    domainset = doNCPost(dict({'Command':'namecheap.domains.dns.setHosts','SLD':'dep10y','TLD':'me','HostName1':'%s%s' % (project['type'],num),'TTL1':'1200','RecordType1':'A','Address1':createdDrop['droplet']['networks']['v4'][0]['ip_address']}.items()+newsets.items()))
    if gh_id:
        firebase.patch('/projects/%s/%s/' % (gh_id, int_id), data={'state': 'Running at %s' % createdDrop['droplet']['name']})
    return createdDrop

def delDroplet(id):
    print('Getting droplet info...')
    createdDrop = doGet('/droplets/%s' % id)
    print createdDrop
    print('Deleting domain entry...')
    newsets = getRecords()
    newnewsets = deepcopy(newsets)
    for rec in newsets:
        if rec.startswith('Address'):
            if newsets[rec] == createdDrop['droplet']['networks']['v4'][0]['ip_address']:
                num = rec[7:]
                del newnewsets['HostName%s' % num]
                del newnewsets['TTL%s' % num]
                del newnewsets['RecordType%s' % num]
                del newnewsets['Address%s' % num]
                if 'MXPref%s' in newnewsets:
                    del newnewsets['MXPref%s' % num]
    domainset = doNCPost(dict({'Command':'namecheap.domains.dns.setHosts','SLD':'dep10y','TLD':'me'}.items()+newnewsets.items()))
    resp = doDelete('/droplets/%s' % id)
    return resp

if __name__ == '__main__':
    firebase = firebase.FirebaseApplication('https://dep10y.firebaseio.com', authentication=None)
    x = firebase.get('/projects', name=None, params=None)
    oldx = deepcopy(x)
    while True:
        x = firebase.get('/projects', name=None, params=None)
        print(x)
        print('old',oldx)
        if not x:
            x = {}
        
        for project in x:
            gh_id = project
            for int_id in x[project].keys():
                otherstuff = x[gh_id][int_id]
                if 'droplet_id' not in otherstuff and otherstuff['state'] == 'Waiting on server':
                    thread = Thread(target = newDroplet, args=(gh_id, int_id))
                    thread.start()

        if not oldx:
            oldx = {}

        for project in oldx:
            gh_id = project
            for int_id in oldx[project].keys():
                deleted = False
                if gh_id not in x:
                    deleted = True
                elif int_id not in x[project]:
                    deleted = True
                if deleted:
                    thread = Thread(target = delDroplet, args=(oldx[gh_id][int_id]['droplet_id'],))
                    thread.start()

        oldx = deepcopy(x)
        time.sleep(4)