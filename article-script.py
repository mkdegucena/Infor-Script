from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from faker import Faker
import requests
import json
import csv
import random
from datetime import datetime

# get configuration
with open('configuration.json') as f:
    data = json.load(f)
# credentials
url = data['config']['url']
email = data['config']['email']
apiKey = data['config']['api_key']

# set var
sectionList = []
userSegmentList = []
startTime = datetime.now()
fake = Faker()

# get the category first we will push it on the first
responseFromCategories = requests.get(url + 'help_center/categories.json?sort_order=asc', auth=(email, apiKey))

if responseFromCategories.status_code == 200:

	dataFromCategories = responseFromCategories.json()
	categoryID = dataFromCategories['categories'][0]['id'];

	responseFromSections = requests.get(url + 'help_center/categories/' + str(categoryID) + '/sections.json?sort_order=asc', auth=(email, apiKey))
	
	if responseFromSections.status_code == 200:
		
		dataFromSections = responseFromSections.json()
		for sections in dataFromSections['sections']:
			sectionList.append(sections['id'])

getArticles = requests.get(url + 'help_center/articles.json', auth=(email, apiKey))


# get the existing user segment list 
with open('userSegmentID.csv', newline='') as csvfile:
    userSegmentList = list(csv.reader(csvfile))

#stats
currentArticleCount = getArticles.json()['count']
totalNeedArticle = data['user_migration_config']['article_count'] - currentArticleCount
createdTicket = 0


def statsFunc():

    global totalNeedArticle,createdTicket
    totalNeedArticle -= 1
    createdTicket += 1

def counterSegmentFunc():

    global counterSegment
    counterSegment += 1

def createIt(url):

	section = random.choice(sectionList)
	segment = random.choice(userSegmentList)[1]

	dataArticle = {"article": {"title": str(fake.sentence()), "body": str(fake.text()) , "locale": str('en-us'),'user_segment_id':str(segment),'draft':'false','permission_group_id':2989974},'notify_subscribers':'false'}
	createArticle = requests.post(url + 'help_center/sections/' + str(section) + '/articles.json',data=json.dumps(dataArticle), auth=(email, apiKey),headers={'content-type': 'application/json'})
	
	if createArticle.status_code == 201:

		statsFunc()
		print("Article #" + str(createArticle.json()['article']['id']) + " created on " + str(datetime.now() - startTime))
		print("Remaining: " + str(totalNeedArticle))
		print("# of Ticket created: " + str(createdTicket))

	else:

		print("Status Code: " + str(createArticle.status_code))
		print(createArticle.json())
		print("Error Occur. Please check the status code. This will still run the article is not created though.")

# stats display
print("Current Article Count: " + str(currentArticleCount))
print("Remaining: " + str(totalNeedArticle))
print("Migration starts!")

# thread start
urls = [url] * totalNeedArticle

with PoolExecutor(max_workers=6) as executor:
    for _ in executor.map(createIt, urls):
        pass