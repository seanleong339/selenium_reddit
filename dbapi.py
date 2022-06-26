from pymongo import MongoClient
from bson import json_util
import datetime
import json
import pandas
import re

def get_by_date(date_start, date_end, news):

    if date_start == None:
        date_start = datetime.datetime.strptime('1990-01-01', '%Y-%m-%d')

    if date_end == None:
        date_end = datetime.datetime.today().strftime('%Y-%m-%d')

    if news:
        result = sgsubmission.find({
            'created_utc': {'$gte': date_start, '$lte': date_end},
            'link_flair_text': {'$eq': 'News'}
        })
    else:
        result = sgsubmission.find({
            'created_utc': {'$gte': date_start, '$lte': date_end},
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