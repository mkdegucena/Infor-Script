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
startTime = datetime.now()
fake = Faker()
sectionList = []
userSegmentList = []
currentArticleCount = 0
createdArticle = 0
totalNeedArticle = 0
secIndexReset = 0

# Current Count, Total Remaining, Created User Segment List
def getData():
	global currentArticleCount,totalNeedArticle,userSegmentList
	# get the some counting
	getArticles = requests.get(url + 'help_center/articles.json', auth=(email, apiKey))
	if getArticles.status_code == 200:
		currentArticleCount = getArticles.json()['count']
		totalNeedArticle = data['migration_config']['article_count'] - currentArticleCount

	# get the existing user segment list 
	with open('userSegmentID.csv', newline='') as csvfile:
		userSegmentList = list(csv.reader(csvfile))

def getAllSectionID():
	# set the first call to get how many pages we need to call
	respSec = requests.get(url + 'help_center/categories/' + str(data['migration_config']['category_id']) + '/sections.json', auth=(email, apiKey))
	secPage = respSec.json()['page_count'] + 1

	#show notif display
	print("We are pulling " + str(secPage) + " pages of sections on this category. Please wait.")
	
	if respSec.status_code == 200:
		# store the 1st call
		storeSectionID(respSec.json())
		# get how many page are we going to call skip the number 1
		for x in range(2,secPage):
			respLoopSec = requests.get(url + 'help_center/en-us/sections.json?page=' + str(x), auth=(email, apiKey))
			if respLoopSec.status_code == 200:
				storeSectionID(respLoopSec.json())

	return True

def storeSectionID(data):
	global sectionList
	for sections in data['sections']:
		sectionList.append(sections['id'])

def statsFunc():
    global totalNeedArticle,createdArticle,secIndexReset
    totalNeedArticle -= 1
    createdArticle += 1
    secIndexReset += 1

def createIt(url):
	global secIndexReset
	print(secIndexReset)
	section = sectionList[secIndexReset];
	totalSection = len(sectionList)
	segment = random.choice(userSegmentList)[1]

	dataArticle = {"article": {"title": str(fake.sentence()), "body": str(fake.text()) , "locale": str('en-us'),'user_segment_id':str(segment),'draft':'false','permission_group_id':2989974},'notify_subscribers':'false'}
	createArticle = requests.post(url + 'help_center/sections/' + str(section) + '/articles.json',data=json.dumps(dataArticle), auth=(email, apiKey),headers={'content-type': 'application/json'})
	
	if createArticle.status_code == 201:
		
		# check reset
		if(secIndexReset == totalSection):
			secIndexReset = -1
		statsFunc()
		
		print("Article #" + str(createArticle.json()['article']['id']) + " created on " + str(datetime.now() - startTime))
		print("Remaining: " + str(totalNeedArticle))
		print("# of Article created: " + str(createdArticle))

	else:
		print("Status Code: " + str(createArticle.status_code))
		print("Error Occur. Please check the status code. This will still run the article is not created though.")


######### START HERE #########
print("Pulling all the sections. Please wait.")

if getAllSectionID():
	# get some data
	getData()
	# stats display
	print("Current Article Count: " + str(currentArticleCount))
	print("Remaining: " + str(totalNeedArticle))
	print("Migration starts!")

	# thread start
	urls = [url] * totalNeedArticle

	with PoolExecutor(max_workers=2) as executor:
	    for _ in executor.map(createIt, urls):
	        pass