'''
Deployed on an AWS EC2 instance it handles passing Facebook leads into Pardot
Next step is to deploy to Lambda to save on costs
'''

#!flask/bin/python
#python2
from flask import Flask, jsonify, abort, request
import requests

app = Flask(__name__)
#user_key = insert your Pardot user key here

#API check it is live
@app.route('/')
def index():
	return "That's when he attacks, not from the front...but from the side"

#With Pardot you need to authorise using username, pass and user key
#You are then given an access key which you can use for your requests
def pardot_auth():
    #Pardot api base URL
	base_url = 'https://pi.pardot.com/api/login/version/4'
	#Should look at moving to env variables
    #email = insert your email user name here
	#password = insert your password here
    
    #authorisation data for POST request to Pardot
	auth_me = {
			"email":email,
			"password":password,
			"user_key":user_key
		}

    #authorisation request to PARDOT
	r = requests.post(base_url, data=auth_me)
    #retrieve the API key for future requests
	position = r.text.find("<api_key>")
    #extract the API key 
	if position != -1:
		api_key = r.text[position+9:position+41]		
		return api_key
	else:
		return "NO KEY"

#Once authorised, send the lead to Pardot
def pardot_send(lead, api_key):
    #Lead set to Facebook
	source = 'facebook'
    #Base URL for adding a lead to pardot
	base_url = 'https://pi.pardot.com/api/prospect/version/4/do/create/email/'
    #Arguments take the form of a GET request
	arguments = '{}&company={}&phone={}&country={}&first_name={}&last_name={}&source={}&user_key={}&api_key={}'.format(lead['email'],lead['company'],lead['phone'],lead['country'],lead['first_name'],lead['last_name'],source,user_key,api_key)
    #make the GET request
    r = requests.get(base_url + arguments)	
    #return the response, need to add validation that the request succeeded
	return r.text

#This is the API to send the leads to from Facebook
@app.route('/raptor', methods=['GET'])
def get_lead(*args):
    
    #Collect the arguments from the GET request
	arguments = request.args
    #Initialise the leads object to hold the leads information
	leads = {}

    #Build leads object
	for key in arguments:
		encoded = arguments[key].encode('ascii', 'ignore')
		leads[key] = encoded

    #insert your password below to avoid unauthorised requests, should set as env variable 
	password = ''
	
    #if the password sent with the request is wrong abort
	if leads['pass'] != password:
		abort(404)
    #if correct then proceed		
	else:
        #Split the fillname passed from Facebook into first and last name
        #first name
         name_split = leads["fullname"].split(" ")
		leads['first_name']= name_split[0]
        #last name, if no last name make a blank space
		if len(name_split) > 1:
			leads['last_name'] = name_split[1]
		else:
			leads['last_name'] = " "
        #authorise and retrive the api key
		api_key = pardot_auth()
        #send the GET request with the lead information
		pardot_send(leads, api_key)
        #return the lead information, should add verification request succeeded
		return jsonify({'leads':leads})

#Launch the app
if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, port=80)
