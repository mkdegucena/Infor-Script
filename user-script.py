from faker import Faker
import requests
import json
import csv

# set the faker data
fake = Faker()

url = "add url here"
email = "add email here/token"
apiKey = "token"

with open('users.csv', 'a') as csvFile:
	# how many user do we need?
	for x in range(0, 100):
		#set a starting point and end point to every 100 for tagging
		startingPoint = x * 100 + 1
		endPoint = startingPoint + 100
		numberTags=[]
		
		# create the tag
		for num in range(startingPoint,endPoint):    
		    numberTags.append(num)
		
		# set and create user
		userCreate = {"user": {"name": str(fake.name()), "email": str(fake.email()),"tags":str(numberTags),"verified":True,"role":"end-user"}}
		postUserCreate = requests.post(url + 'users.json', data=json.dumps(userCreate), auth=(email, apiKey),headers={'content-type': 'application/json'})
		
		if postUserCreate.status_code == 201:
			# save to csv
			user = postUserCreate.json()
			print(str(user['user']['email']) + " created.")
			writer = csv.writer(csvFile)
			writer.writerow([user['user']['email'],'123456'])
		else:
			print(postUserCreate.status_code)
			
		# make sure we clear every
		del numberTags[:]
	
csvFile.close()
