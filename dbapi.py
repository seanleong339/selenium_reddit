from pymongo import MongoClient
from bson import json_util
import datetime
import json
import pandas
import re

def get_by_date(date_start, date_end, news):

    if not date_start:
        print('test')
        date_start = '1990-01-01'
        print(date_start)

    if not date_end:
        print('test;')
        date_end = datetime.datetime.today().strftime('%Y-%m-%d')
        print(date_end)

    if news == '1':
        result = sgsubmission.find({
            'created_utc': {'$gte': date_start, '$lte': date_end},
            'link_flair_text': {'$eq': 'News'}
        })
    else:
        result = sgsubmission.find({
            'created_utc': {'$gte': date_start, '$lte': date_end},
            'link_flair_text': {'$ne': 'News'}
        })
    
    return list(result)

def get_comments(linkid):
    post = sgsubmission.find({
        'id': linkid
    })
    comments = sgcomment.find({
        'link_id': linkid
    })
    result = list(post)
    result = result + list(comments)

    return result

def get_users():
    users = sgsubmission.distinct('author')
    return list(users)

client = MongoClient('localhost', 27017)

db = client.Reddit

sgsubmission = db['Submission']
sgcomment = db['Comments']

cmd = input('Enter 1 for submissions, 2 for comments, 3 for userids: ')

while not cmd.isdigit() or (int(cmd) < 0 or int(cmd) > 4) :
    cmd = input('Please enter a number. Enter 1 for submissions, 2 for comments, 3 for userids: ')

if int(cmd) == 1:
    datereg = '^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
    # input time range that tweets are from, in yyyy-mm-dd format
    date_start = input('Start of date range in yyyy-mm-dd format: ') #inclusive

    while date_start and not re.match(datereg,date_start):
        date_start = input('Please input start of date range in yyyy-mm-dd format: ') 
    if date_start == '':
        date_start = None
    
    date_end = input('End of date range in yyyy-mm-dd format: ') #not inclusive
    while date_end and not re.match(datereg, date_end):
        date_end = input('Please input end of date range in yyyy-mm-dd format: ') 
    if date_end == '':
        date_end = None

    region = input('Enter region, 1 for Singapore: ')
     
    while not region.isdigit() or (int(region) < 0 or int(region) > 1) :
        region = input('Please enter a number. Enter 1 for Singapore: ')
    
    news = input('Enter 1 for news, 0 for non-news: ')
    while not news.isdigit() or (int(news) < 0 or int(news) > 1):
        news = input('Enter 1 for news, 0 for non-news: ')
    
    data = get_by_date(date_start, date_end, news)
    
if int(cmd) == 2:
    convoid = input('Enter the submission Id: ')
    region = input('Enter region, 1 for Singapore: ')
     
    while not region.isdigit() or (int(region) < 0 or int(region) > 1) :
        region = input('Please enter a number. Enter 1 for Singapore: ')
    
    data = get_comments(convoid)

if int(cmd) == 3:
    data = get_users()

#data = get_by_date('2022-05-06', '2022-05-07', True)

#data = get_comments('ujotg7')

#data = get_users()

num = len(data)

print(num)

data = json_util.dumps(data, indent=4)

data = json.loads(data)

with open('myfile.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f'{num} results written to myfile')