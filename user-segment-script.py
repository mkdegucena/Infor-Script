import requests
import json
import csv

# get configuration
with open('configuration.json') as f:
    data = json.load(f)
# credentials
url = data['config']['url']
email = data['config']['email']
apiKey = data['config']['api_key']

with open('userSegmentID.csv','r+') as csvFile:

	continueCount = 0
	# get where we stopped
	for row in reversed(list(csv.reader(csvFile))):
		continueCount = continueCount + int(row[0]) + 1
		break

	for x in range(int(continueCount), data['user_segment_config']['segment_range']):
		userSegment = {"user_segment": {"name": "User Segment #" + str(x),"user_type": "signed_in_users","tags":[x]}}
		postUserSegmentCreate = requests.post(url + 'help_center/user_segments.json', data=json.dumps(userSegment), auth=(email, apiKey),headers={'content-type': 'application/json'})
		
		if postUserSegmentCreate.status_code == 201:
			segment = postUserSegmentCreate.json()
			writer = csv.writer(csvFile)
			writer.writerow([x,segment['user_segment']['id']])
			print(str(segment['user_segment']['name']) + " created.")
		else:
			print(postUserSegmentCreate.status_code)
			print(postUserSegmentCreate.json())

csvFile.close()
