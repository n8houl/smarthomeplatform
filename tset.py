import http.client
from urllib.parse import urlparse

import sys
import json


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
			raise Exception("Redirect with non 200 response")

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
			raise Exception("Redirect with non 200 response")
	data = response.read()
	return data.decode("utf-8")

print(getToken(client_id, client_secret, grant_type, code))
#print(get("/devices/thermostats/1eNZXbW1J0bFp-OmrOwz7w0IofQbe_-8/target_temperature_f"))
#print(put("/devices/thermostats/1eNZXbW1J0bFp-OmrOwz7w0IofQbe_-8", "{ \"target_temperature_f\": 70 }"))
