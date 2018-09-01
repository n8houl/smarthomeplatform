import http.client
from urllib.parse import urlparse

import sys
import json

import base64
import uuid

import threading

token = ""
url = "use1-wap.tplinkcloud.com"

with open("token_tpl", "r") as f:
	token = f.readline().replace('\n', '')

# First use
def load_un_pass(fn):
	enc = ""
	with open(fn, 'r') as f:
		enc = f.readline().rstrip()

	unpass = str(base64.b64decode(enc), 'utf-8').rstrip()
	un = unpass.split('\n')[0]
	pss = unpass.split('\n')[1]
	return un, pss

def get_token(un, pss):
	guid = str(uuid.uuid4())
	login_obj = {
		"method": "login",
		"params": {
			"appType": "Kasa_Android",
			"cloudPassword": pss,
			"cloudUserName": un,
			"terminalUUID": guid
		}
	}
	
	payload = json.dumps(login_obj)
	conn = http.client.HTTPSConnection("wap.tplinkcloud.com")
	headers = {'Content-Type': "application/json"}
	conn.request("POST", "", payload, headers)

	response = conn.getresponse()

	data = response.read()

	response_obj = json.loads(data.decode("utf-8"))
	result = response_obj['result']
	token = result['token']

	return token

def tpl_post(deviceId, data):
	req_obj = {
		"method": "passthrough",
		"params": {
			"deviceId": deviceId,
			"requestData": "{\"system\": {%s}}" % data
		}
	}

	payload = json.dumps(req_obj)
	conn = http.client.HTTPSConnection(url)
	headers = {'Content-Type': "application/json"}
	conn.request("POST", "/?token=%s" % token, payload, headers)

	response = conn.getresponse()
	
	return response.read()

def get_sysinfo(deviceId):
	data = tpl_post(deviceId, "\"get_sysinfo\":null")

	response_obj = json.loads(data.decode("utf-8"))

	result = response_obj['result']
	responseData = result['responseData']

	responseDataObj = json.loads(responseData)
	system = responseDataObj['system']
	get_sysinfo = system['get_sysinfo']
	
	return get_sysinfo

def get_device_status(deviceId):
	sysinfo = get_sysinfo(deviceId)
	relay_state = sysinfo['relay_state']

	return int(relay_state)

def get_device_alias(deviceId):
	sysinfo = get_sysinfo(deviceId)
	device_alias = sysinfo['alias']

	return device_alias

def set_device_status(deviceId, val):
	data = tpl_post(deviceId, "\"set_relay_state\":{\"state\":%d}" % val)
	
	response_obj = json.loads(data.decode("utf-8"))
	
	result = response_obj['result']
	responseData = json.loads(result['responseData'])
	
	system = responseData['system']
	set_relay_state = system['set_relay_state']
	err_code = int(set_relay_state['err_code'])
	
	if err_code != 0:
		raise Exception('Error setting swtich to %d' % val)
	else:
		print('Set switch to %d' % val)
	
def t_listen_for_plug_changes(deviceId):
	status = get_device_status(deviceId)
	while True:
		new_status = get_device_status(deviceId)
		if status != new_status:
			print(new_status)
			status = new_status

def listen_for_plug_changes(deviceId):
	t = threading.Thread(target=t_listen_for_plug_changes, args=(deviceId,))
	t.start()

print(get_device_alias("800623901FDDF95AC226FF5C98B3CD10195FFF33"))
print(get_device_status("800623901FDDF95AC226FF5C98B3CD10195FFF33"))

set_device_status("800623901FDDF95AC226FF5C98B3CD10195FFF33", 0)

listen_for_plug_changes("800623901FDDF95AC226FF5C98B3CD10195FFF33")

while True:
	pass
