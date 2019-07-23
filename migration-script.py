from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from faker import Faker
import requests
import json
import random
from datetime import datetime

# set the faker data
fake = Faker()

# data requirments for the requests
url = "https://z3n-infortest.zendesk.com/api/v2/"
email = "mdegucena@zendesk.com/token"
apiKey = "U5UJl5Kj3IxpBPNr9UH05Q6X0CUaLHpOk9FXwaJD"

# data requirments for the requests
url = "https://z3n-infortest.zendesk.com/api/v2/"
email = "mdegucena@zendesk.com/token"
apiKey = "U5UJl5Kj3IxpBPNr9UH05Q6X0CUaLHpOk9FXwaJD"

# where we will push the random articles
sectionList = []
startTime = datetime.now()


# get the category first
responseFromCategories = requests.get(url + 'help_center/categories.json?sort_order=asc', auth=(email, apiKey))
	
if responseFromCategories.status_code == 200:
	# since we only have one category get the 1st id
	dataFromCategories = responseFromCategories.json()
	categoryID = dataFromCategories['categories'][0]['id'];
	
	# get all the section and put it in an array
	responseFromSections = requests.get(url + 'help_center/categories/' + str(categoryID) + '/sections.json?sort_order=asc', auth=(email, apiKey))
	if responseFromSections.status_code == 200:
		dataFromSections = responseFromSections.json()
		for sections in dataFromSections['sections']:
			sectionList.append(sections['id'])

#get here the current count of the articles
getArticles = requests.get(url + 'help_center/articles.json', auth=(email, apiKey))

# set the stats
currentArticleCount = getArticles.json()['count']
totalNeedArticle = 1500000 - currentArticleCount
createdTicket = 0

# set it global
def statsFunc():
    global totalNeedArticle,createdTicket
    totalNeedArticle -= 1
    createdTicket += 1

# set a display of stats
print("Current Article Count: " + str(currentArticleCount))
print("Remaining: " + str(totalNeedArticle))
print("Migration starts!")


def createIt(url):
	section = random.choice(sectionList)
	
	# create the article
	dataArticle = {"article": {"title": str(fake.sentence()), "body": str(fake.text()) , "locale": str('en-us'),'user_segment_id':None,'draft':'false','permission_group_id':2989974},'notify_subscribers':'false'}
	createArticle = requests.post(url + 'help_center/sections/' + str(section) + '/articles.json',data=json.dumps(dataArticle), auth=(email, apiKey),headers={'content-type': 'application/json'})
	if createArticle.status_code == 201:
		statsFunc()
		print("Ticket #" + str(createArticle.json()['article']['id']) + " created on " + str(datetime.now() - startTime))
		print("Remaining: " + str(totalNeedArticle))
		print("# of Ticket created: " + str(createdTicket))
	else:
		print("Status Code: " + str(createArticle.status_code))
		# print(createArticle.json())
		print("Error Occur. Please check the status code. This will still run the article is not created though.")
	
urls = [url] * totalNeedArticle

with PoolExecutor(max_workers=2) as executor:
    for _ in executor.map(createIt, urls):
        pass