#!flask/bin/python
from flask import Flask, jsonify, abort, request
import requests

app = Flask(__name__)
#user_key = insert your Pardot user key here


@app.route('/')
def index():
	return "That's when he attacks, not from the front...but from the side"

def pardot_auth():
	base_url = 'https://pi.pardot.com/api/login/version/4'
	#email = insert your email user name here
	#password = insert your password here

	auth_me = {
			"email":email,
			"password":password,
			"user_key":user_key
		}

	r = requests.post(base_url, data=auth_me)
	print r.text
	position = r.text.find("<api_key>")
	print position
	if position != -1:
		api_key = r.text[position+9:position+41]		
		return api_key
	else:
		return "NO KEY"

def pardot_send(lead, api_key):
	source = 'facebook'
	base_url = 'https://pi.pardot.com/api/prospect/version/4/do/create/email/'
	arguments = '{}&company={}&phone={}&country={}&first_name={}&last_name={}&source={}&user_key={}&api_key={}'.format(lead['email'],lead['company'],lead['phone'],lead['country'],lead['first_name'],lead['last_name'],source,user_key,api_key)
	r = requests.get(base_url + arguments)	
	return r.text

@app.route('/raptor', methods=['GET'])
def get_lead(*args):

	arguments = request.args
	leads = {}

	for key in arguments:
		encoded = arguments[key].encode('ascii', 'ignore')
		leads[key] = encoded

	#password = insert your password here to prevent unauthorised requests
	
	if leads['pass'] != password:
		abort(404)		
	else:
		name_split = leads["fullname"].split(" ")
		leads['first_name']= name_split[0]
		if len(name_split) > 1:
			leads['last_name'] = name_split[1]
		else:
			leads['last_name'] = " "

		api_key = pardot_auth()
		pardot_send(leads, api_key)
		return jsonify({'leads':leads})


if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, port=80)
