
import time, urllib.request
from tracemalloc import start
import re
import os
import json
import praw
import requests
import datetime as dt
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
from psaw import PushshiftAPI

reddit = praw.Reddit(
client_id="1aMqUjUXh1_OU_iV2lTBmQ",
client_secret="YmB7r_gGFj1zX5XMvGo4bS1aSeOiXw",
user_agent="linux:tryingitout:1 (by /u/georgefoo782)",
)


api = PushshiftAPI()

listid = []

start_epoch=int(dt.datetime(2022, 6, 14).timestamp())

sample = list(api.search_submissions(before=start_epoch,
							subreddit='singapore',
							filter=['id'],
							limit=200))


for post in sample:
	listid.append(post.d_['id'])

fullnames = [f"t3_{id}" for id in listid]

tic = time.perf_counter()

for i, submission in enumerate(reddit.info(fullnames=fullnames)):
	fulltext = {}
	print(f"Processing post:{i}, with ID: {submission.id}")
	id = submission.id
	post_time = dt.datetime.fromtimestamp(submission.created_utc)
	timeforpath = post_time.strftime("%m%d%Y-%H%M")
	downloadpath = 'downloads/fast/{}-{}'.format(timeforpath,id)
	selftext = submission.selftext

	if selftext == '[removed]' or selftext == '[deleted]':
		continue

	if not os.path.isdir(downloadpath):
		os.makedirs(downloadpath)

	score = submission.score
	upvote_ratio = submission.upvote_ratio
	downvote_ratio = round(1-upvote_ratio,2)
	downvotes = round((score/upvote_ratio)*downvote_ratio)
	fulltext['Title'] = submission.title
	fulltext['Text'] = selftext
	
	if not submission.is_self:
		fulltext['Url']= submission.url
	fulltext["Submission_time"] = post_time
	fulltext["Upvote ratio"] = upvote_ratio
	fulltext["Score"] = score
	fulltext["Downvotes"] = downvotes
	
	resp = requests.get("https://www.reddit.com/{}/.json".format(id), headers= {'User-agent': 'linux:tryingitout:1 (by /u/georgefoo782)'})
	site = resp.json()
	posthint = site[0]['data']['children'][0]['data'].get('post_hint',None)
	if posthint == 'image':
		try:
			urllib.request.urlretrieve(resp.json()[0]['data']['children'][0]['data']['url'], '{}/{}.jpg'.format(downloadpath,id))
		except:
			print('Img deleted')

	fulltext['Comments'] = []

	for top_level_comment in submission.comments:
		if isinstance(top_level_comment, MoreComments):
			continue
		comment = top_level_comment
		author = top_level_comment.author
		comment_time = dt.datetime.fromtimestamp(comment.created_utc)
		if author is not None:
			name = author.name
		else:
			name = 'Hidden'
		if comment is not None:
			fulltext['Comments'].append({"Commenter":name,"Comment":top_level_comment.body,"Time":comment_time})

	#Save text to JSON file 
	with open('{}/{}.json'.format(downloadpath,id), 'w',encoding='utf-8') as file:
		json.dump(fulltext, file, ensure_ascii=False, indent=4, default=str)

toc = time.perf_counter()
print(f"Downloaded 200 submissions in {toc - tic:0.4f} seconds")