from faker import Faker
import requests
import json
import csv

# set the faker data
fake = Faker()

# get configuration
with open('configuration.json') as f:
    data = json.load(f)
# credentials
url = data['config']['url']
email = data['config']['email']
apiKey = data['config']['api_key']

with open('users.csv', 'a') as csvFile:

	for x in range(0, data['user_script_config']['user_range']):

		#set a starting point and end point to every 100 for tagging
		startingPoint = x * 100 + 1
		endPoint = startingPoint + 100
		numberTags=[]
		
		# create the tag
		for num in range(startingPoint,endPoint):    
		    numberTags.append(num)

		userCreate = {"user": {"name": str(fake.name()), "email": str(fake.email()),"tags":str(numberTags),"verified":True,"role":"end-user"}}
		postUserCreate = requests.post(url + 'users.json', data=json.dumps(userCreate), auth=(email, apiKey),headers={'content-type': 'application/json'})
		
		if postUserCreate.status_code == 201:

			user = postUserCreate.json()
			changePW = {"password": data['user_script_config']['default_password']}
			changePasswordRequest = requests.post(url + 'users/' + str(user['user']['id']) + '/password.json', data=json.dumps(changePW), auth=(email, apiKey),headers={'content-type': 'application/json'})
			
			if changePasswordRequest.status_code == 200:

				writer = csv.writer(csvFile)
				writer.writerow([user['user']['email'],data['user_script_config']['default_password']])
				print(str(user['user']['email']) + " created and change the password.")
		else:
			print(postUserCreate.status_code)

		# make sure we clear every loop
		del numberTags[:]
	
csvFile.close()
