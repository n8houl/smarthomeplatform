import http.client
from urllib.parse import urlparse

import sys
import json

import _thread

token = ""
with open("token_nest", "r") as f:
	token = f.readline().replace('\n', '')

def get_target_temperature(therm):
	return get("/devices/thermostats/%s/target_temperature_f" % therm)

def set_target_temperature(therm, temp):
	body = "{ \"target_temperature_f\": %d }" % temp
	return put("/devices/thermostats/%s" % therm, body)

# First Use
def getToken(client_id, client_secret, grant_type, code):
	conn = http.client.HTTPSConnection("api.home.nest.com")
	headers = {'Content-Type': "application/x-www-form-urlencoded"}
	body="client_id=%s&client_secret=%s&grant_type=%s&code=%s" % (client_id, client_secret, grant_type, code)
	conn.request("POST", "/oauth2/access_token", body, headers)
	response = conn.getresponse()
	
	if response.status == 307:
		redirectionLocation = urlparse(response.getheader("location"))
		conn = http.client.HTTPSConnection(redirectionLocation)
		conn.request("POST", "/oath2/access_token", body, headers)
		response = conn.getresponse()
		if response.status != 200:
			raise Exception("Redirect with non 200 response")
	data = response.read()
	strjson = data.decode("utf-8")	
	
	jsobj = json.loads(strjson)
	
	if 'access_token' not in jsobj.keys():
		raise Exception("%s: %s, Instance: %s" % (jsobj['error'], jsobj['error_description'], jsobj['instance_id']))
	else:
		return jsobj['access_token']

def get(url):
	conn = http.client.HTTPSConnection("developer-api.nest.com")
	headers = {'authorization': "Bearer {0}".format(token)}
	conn.request("GET", "{0}".format(url), headers=headers)
	response = conn.getresponse()

	if response.status == 307:
		redirectLocation = urlparse(response.getheader("location"))
		conn = http.client.HTTPSConnection(redirectLocation.netloc)
		conn.request("GET", "{0}".format(url), headers=headers)
		response = conn.getresponse()
		if response.status != 200:
			raise Exception("Redirect with non 200 response.")

	data = response.read()
	return data.decode("utf-8")

def put(url, body):
	conn = http.client.HTTPSConnection("developer-api.nest.com")
	headers = {'authorization': "Bearer {0}".format(token)}
	conn.request("PUT", url, body, headers)
	response = conn.getresponse()

	if response.status == 307:
		redirectLocation = urlparse(response.getheader("location"))
		conn = http.client.HTTPSConnection(redirectLocation.netloc)
		conn.request("PUT", url, body, headers)
		response = conn.getresponse()
		if response.status != 200:
			raise Exception("Redirect with non 200 response. Response: %s" % response.status)
	data = response.read()
	return data.decode("utf-8")

# Change this to rest streaming, more real time, avoids too many request error
def listen_for_temp_change(name, therm):
	t = int(get_target_temperature(therm))
	while True:
		new_t = int(get_target_temperature(therm))
		if t != new_t:
			print(new_t)
			t = new_t

def do_listen_for_temp_change(therm):
	try:
		_thread.start_new_thread(listen_for_temp_change, ('Thread-2', therm,))
	except:
		print('Error opening thread')

do_listen_for_temp_change('1eNZXbW1J0bFp-OmrOwz7w0IofQbe_-8')

#print(getToken(client_id, client_secret, grant_type, code))
print(get_target_temperature('1eNZXbW1J0bFp-OmrOwz7w0IofQbe_-8'))
print(set_target_temperature('1eNZXbW1J0bFp-OmrOwz7w0IofQbe_-8', 72))
#print(put("/devices/thermostats/1eNZXbW1J0bFp-OmrOwz7w0IofQbe_-8", "{ \"target_temperature_f\": 70 }"))

while True:
	pass
