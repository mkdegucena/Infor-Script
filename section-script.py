from faker import Faker
import requests
import json

fake = Faker()

# get configuration
with open('configuration.json') as f:
    data = json.load(f)
# credentials
url = data['config']['url']
email = data['config']['email']
apiKey = data['config']['api_key']

for x in range(500):
	dataSection = {"section": {"locale": "en-us", "name": str(fake.sentence())}}
	createSection = requests.post(url + 'help_center/categories/' + data['section_config']['category_id'] + '/sections.json',data=json.dumps(dataSection), auth=(email, apiKey),headers={'content-type': 'application/json'})
	if createSection.status_code == 201:
		print("Created:" + str(createSection.json()['section']['id']))