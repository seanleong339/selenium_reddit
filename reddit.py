import time, urllib.request
import requests
import os
import json
import praw
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from praw.models import MoreComments

WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(
	service=Service(ChromeDriverManager().install()), options=chrome_options
)

driver.get("https://www.reddit.com/r/singapore")  # input reddit page or subreddit

#scroll down
scrolldown=driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
for x in range(1):
	last_count = scrolldown
	time.sleep(3)
	scrolldown = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
print(driver.title)
	
search_results = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "rpBJOHq2PR60pnwJlUyP0")))

posts = []
content = driver.page_source
soup = BeautifulSoup(content, "html.parser")
articles = soup.find_all("div", {"data-testid":"post-container"})
links = []
for article in articles:
	links.append('http://reddit.com'+ article.find("a", {"data-click-id": "body"}).get("href"))
	
	
print(len(links))

reddit = praw.Reddit(
client_id="1aMqUjUXh1_OU_iV2lTBmQ",
client_secret="YmB7r_gGFj1zX5XMvGo4bS1aSeOiXw",
user_agent="linux:tryingitout:1 (by /u/georgefoo782)",
)

for link in links:
	time.sleep(5)
	driver.get(link)
	time.sleep(5)
	content = driver.page_source
	soup = BeautifulSoup(content, "html.parser")
	jsonsource = driver.get(link+'.json')
	jsonsource = driver.page_source
	jsonsoup = BeautifulSoup(jsonsource, 'html.parser')
	pagejson = jsonsoup.find('pre').get_text()
	pagejson = json.loads(pagejson)
	
	subreddit = pagejson[0]['data']['children'][0]['data']['subreddit']
	download_path_page = 'downloads/' + subreddit

	# create folder
	title = soup.find("h1").get_text().replace('/', '').replace(' ', '-')
	if len(title) > 20:
		title = title[0:20]
	download_path = download_path_page + "/" + title
	if not os.path.isdir(download_path):
		os.makedirs(download_path)

	data = soup.find("div", {"data-test-id": "post-content"})
	user = data.find('a', {'data-click-id':'user'}).get_text()
	
	#Extract caption if exist
	maincaption = data.find_all('p')
	if maincaption is not None:
		caption = ''
		for caps in maincaption:
			caption += caps.get_text()
			
	#Store text info
	fulltext = {'Author':user, 'Title':title, 'Caption':caption}
	
	#Extract lone img
	metacontent = soup.find('meta', {'property':'og:image'})
	if metacontent is not None:
		metacontent = metacontent.get('content')
		urllib.request.urlretrieve(metacontent, '{}/{}.jpg'.format(download_path,title))
	
	#Extract video if exist
	try:
		videolink = pagejson[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["dash_url"]
		urllib.request.urlretrieve(videolink, '{}/{}.mp4'.format(download_path,'vid'))
	except Exception as e:
		print("No video link found")
	
	#Extract img gallery if exist
	gallery = data.find('ul')
	if gallery is not None:
		images = gallery.find_all('img')
		count = 0
		for image in images:
			count += 1
			imglink = image.get('src')
			urllib.request.urlretrieve( imglink, '{}/{}({}).jpg'.format(download_path,'pic',count))
			time.sleep(5)
	
	#Extract external link if exists
	external = data.find('a', {'data-testid':'outbound-link'})
	if external is not None:
		externallink = external.get('href')
		fulltext['External link'] = externallink
	

	url = link
	submission = reddit.submission(url=url)
	post_time = datetime.datetime.fromtimestamp(submission.created_utc)
	score = submission.score
	upvote_ratio = submission.upvote_ratio
	downvote_ratio = round(1-upvote_ratio,2)
	downvotes = round((score/upvote_ratio)*downvote_ratio)
	fulltext["Submission_time"] = post_time
	fulltext["Upvote ratio"] = upvote_ratio
	fulltext["Score"] = score
	fulltext["Downvotes"] = downvotes
	
	fulltext['Comments'] = []

	for top_level_comment in submission.comments:
		if isinstance(top_level_comment, MoreComments):
			continue
		comment = top_level_comment
		author = top_level_comment.author
		comment_time = datetime.datetime.fromtimestamp(comment.created_utc)
		if author is not None:
			name = author.name
		else:
			name = 'Hidden'
		if comment is not None:
			fulltext['Comments'].append({"Commenter":name,"Comment":top_level_comment.body,"Time":comment_time})
		
		
	#Save text to JSON file 
	with open(os.path.join(download_path, 'text.json'), 'w') as file:
		json.dump(fulltext, file, ensure_ascii=False, indent=4, default=str)
		
	
driver.close()
		
