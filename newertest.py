import time, urllib.request
from tracemalloc import start
import re
import pandas as pd
import os
import json
import praw
import requests
import numpy
import datetime as dt
from tqdm import tqdm
from bs4 import BeautifulSoup
from pmaw import PushshiftAPI
from praw.models import MoreComments


reddit = praw.Reddit(
client_id="1aMqUjUXh1_OU_iV2lTBmQ",
client_secret="YmB7r_gGFj1zX5XMvGo4bS1aSeOiXw",
user_agent="linux:tryingitout:1 (by /u/georgefoo782)",
)


#api = PushshiftAPI(praw=reddit)
api = PushshiftAPI()

listid = []

start_epoch=int(dt.datetime(2020,5,7).timestamp()) #yyyy mm dd
end_epoch = start_epoch - (86400*10)
total = 0

tic = time.perf_counter()

while total < 25000:
	sample = list(api.search_submissions(before=start_epoch, after=end_epoch,
								subreddit='singapore',
								limit=30000
								))
	
	count = len(sample)
	print(f'{count} from {dt.datetime.fromtimestamp(start_epoch)} to {dt.datetime.fromtimestamp(end_epoch)}')
	print(f'starting from {dt.datetime.fromtimestamp(sample[0]["created_utc"])}')
	if count > 100:
		start_epoch = int(sample[0]['created_utc'])
		end_epoch = start_epoch - (86400*10) #subtract by 10 days in seconds
	else:
		print(f'{dt.datetime.fromtimestamp(start_epoch)} to {dt.datetime.fromtimestamp(end_epoch)} has < 100 submissions')
		start_epoch = end_epoch
		end_epoch = end_epoch - (86400*10)

	total += count
	listid = listid + sample


print(len(listid))


sub_df = pd.DataFrame(listid)

#Remove duplicates
sub_df = sub_df.loc[sub_df.astype(str).drop_duplicates().index]

print(f'{total - sub_df.shape[0]} duplicates removed')

#Remove removed submissions
#sub_df = sub_df[pd.isnull(sub_df['removed_by_category'])]
#num_left = sub_df.shape[0]

#print(f'{total-num_left} submissions removed')

sub_df['created_utc'] = pd.to_datetime(sub_df['created_utc'], unit='s')

try:
	sub_df.to_json('submission.json', orient='records',date_format= 'iso', force_ascii=False)
except Exception as e:
	print(e)

toc = time.perf_counter()
print(f"Downloaded {sub_df.shape[0]} submissions in {toc - tic:0.4f} seconds")

sub_ids = list(sub_df.loc[:, 'id']) 

# retrieve comment ids for submissions
tic = time.perf_counter()

comments = api.search_submission_comment_ids(ids=sub_ids) 

comments = list(comments)

# retrieve comments by id

comments_df = pd.DataFrame(comments)

numcom = comments_df.shape[0]

#Remove 't3_' from link_id

if not comments_df.empty:
	comments_df['link_id'] = comments_df['link_id'].str.replace(r'^t3_','', regex=True)
	
	comments_df['created_utc'] = pd.to_datetime(comments_df['created_utc'], unit='s')
	
	
	comments_df.to_json('comments.json', orient='records', date_format= 'iso',force_ascii=False)

print('test')
toc = time.perf_counter()
print(f"Downloaded {numcom} comments or {len(sub_ids)} submissions worth in {toc - tic:0.4f} seconds")



"""
for submission in tqdm(listid):
	if submission['selftext'] == '[removed]':
		continue
	fulltext = {}
	id = submission['id']
	post_time = dt.datetime.fromtimestamp(submission['created_utc'])
	score = submission['score']
	upvote_ratio = submission['upvote_ratio']
	downvotes = submission['downs']
	upvotes = submission['ups']
	fulltext['Title'] = submission['title']
	fulltext['Text'] = submission['selftext']
	fulltext['Url'] = submission['url']
	fulltext['Author'] = submission['author']
	fulltext['Submission_time'] = post_time
	fulltext['Upvote_ratio'] = upvote_ratio
	fulltext['Upvotes'] = upvotes
	fulltext['Downvotes'] = downvotes
	downloadpath = f'pmaw/{post_time.strftime("%Y%m%d-%H%M")}-{id}'

	if not os.path.isdir(downloadpath):
		os.makedirs(downloadpath)

	if submission.get('post_hint') == 'image':
		urllib.request.urlretrieve(submission['url'], f'{downloadpath}/{id}.jpg')

	resp = requests.get(f"https://api.pushshift.io/reddit/comment/search?limit=100&q=*&link_id={id}")
	comments = resp.json()["data"]
	df_comment = pd.DataFrame(comments)
	if not df_comment.empty:
		short_df = df_comment.loc[:,['author','body','created_utc']]
		short_df['created_utc'] = pd.to_datetime(short_df['created_utc'], unit='s')
		short_df.columns = ['Author', 'Text', 'Comment_time']
		fulltext['Comments'] = short_df.to_dict('records')
	else:
		fulltext['Comments'] = None

	with open(f'{downloadpath}/{id}.json', 'w',encoding='utf-8') as file:
		json.dump(fulltext, file, ensure_ascii=False, indent=4, default=str)


"""