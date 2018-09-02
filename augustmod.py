import http.client
from urllib.parse import urlparse

import sys
import json
import time

import base64
import uuid

import threading


headers = {
	"Accept-Version": "0.0.1",
	"x-august-api-key": "79fd0eb6-381d-4adf-95a0-47721289d1d9",
	"x-kease-api-key": "79fd0eb6-381d-4adf-95a0-47721289d1d9",
	"Content-Type": "application/json",
	"User-Agent": "August/Luna-3.2.2"
}

username = ""
password = ""

installId = str(uuid.uuid4())

def load_un_pass(fn):
	enc = ""
	with open('creds_aug', 'r') as f:
		enc = f.readline().rstrip()
	
	unpass = str(base64.b64decode(enc), 'utf-8').rstrip()
	un = unpass.split('\n')[0]
	pss = unpass.split('\n')[1]
	global username
	username = un
	global password
	password = pss
	return un, pss

def auth(auth):
	if auth == "authenticated":
		return auth
	with open('token_august', 'r') as f:
		line = f.readline()
		if line != '' and line is not None:
			obj = json.loads(line)

		if line != '' and line is not None and obj['x-august-access-token'] is not  None and obj['x-august-access-token'] != '' and obj['auth_status'] == "authenticated":
			headers['x-august-access-token'] = obj['x-august-access-token']
			authentication_status = "authenticated"		
			return "authenticated"

	un, pss = load_un_pass('creds_aug')

	payload = {
		"installId": installId,
		"identifier": "email:%s" % un,
		"password": pss
	}

	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("POST", "/session", json.dumps(payload), headers)

	response = conn.getresponse()
	h = response.headers
	data = json.loads(response.read().decode('utf-8'))

	token = h['x-august-access-token']

	headers['x-august-access-token'] = token

	if data['vPassword'] and data['vInstallId']:
		with open('token_august', 'w') as f:
			js = {
				"installId": installId,
				"x-august-access-token": token,
				"auth_status": "authenticated"
			}
			f.write(json.dumps(js))
			
		return "authenticated"
	return "not_authenticated"

def send_code(authentication_status, un):
	if authentication_status == "authenticated":
		return

	payload = {
		"value": un
	}

	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("POST", "/validation/email", json.dumps(payload), headers)

	response = conn.getresponse()
	h = response.headers
	data = response.read().decode('utf-8')
	
	print(h)
	print(data)

def verify_code(authentication_status, un, code):
	if authentication_status == "authenticated":
		return

	payload = {
		"email": un,
		"code": str(code)
	}

	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("POST", "/validate/email", json.dumps(payload), headers)
	
	response = conn.getresponse()
	h = response.headers
	data = response.read().decode('utf-8')
	
	print(h)
	print(data)

def get_houses():
	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("GET", "/users/houses/mine", headers=headers)

	response = conn.getresponse()
	data = json.loads(response.read().decode('utf-8'))
	
	houses = []

	for i in data:
		if i['type'] == "superuser":
			houses.append(i['HouseID'])			

	return houses

def get_locks():
	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("GET", "/users/locks/mine", headers=headers)

	response = conn.getresponse()
	data = json.loads(response.read().decode('utf-8'))
	
	houseIds = get_houses()

	locks = []
	for i in data.keys():
		if data[i]['HouseID'] in houseIds:
			locks.append(i)
	
	return locks

def unlock(lockid):
	payload = {
		"status": "kAugLockState_Unlocked"
	}
	
	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("PUT", "/remoteoperate/%s/unlock" % lockid, json.dumps(payload), headers)

	response = conn.getresponse()
	data = response.read().decode('utf-8')

	return data

def lock(lockid):
	payload = {
		"status": "kAugLockState_Locked"
	}

	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("PUT", "/remoteoperate/%s/lock" % lockid, json.dumps(payload), headers)
	
	response = conn.getresponse()
	data = response.read().decode('utf-8')

	return data

def get_lock_status(lockid):
	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("GET", "/locks/%s/status" % lockid, headers=headers)

	response = conn.getresponse()
	data = json.loads(response.read().decode('utf-8'))

	return data['status']

def get_lock_details(lockid):
	conn = http.client.HTTPSConnection("api-production.august.com")
	conn.request("GET", "/locks/%s" % lockid, headers=headers)

	response = conn.getresponse()
	data = json.loads(response.read().decode('utf-8'))
	
	return data

def get_lock_battery_status(lockid):
	lock = get_lock_details(lockid)
	return int(float(lock['battery']) * 100)

def get_lock_name(lockid):
	lock = get_lock_details(lockid)
	return lock['LockName']

authentication_status = auth("not_authenticated")
send_code(authentication_status, username)
if authentication_status == "not_authenticated":
	code = int(input("Enter code: "))
	verify_code(authentication_status, username, code)
authentication_status = auth(authentication_status)

print(authentication_status)
houses = get_houses()
for house in houses:
	print(house)

locks = get_locks()

#print(unlock(locks[0]))

#time.sleep(5)

#print(lock(locks[0]))

print(get_lock_status(locks[0]))

print(get_lock_battery_status(locks[0]))

print(get_lock_name(locks[0]))
