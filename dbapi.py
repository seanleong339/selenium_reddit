from pymongo import MongoClient
from bson import json_util
import datetime
import json
import pandas
import re

def get_by_date(date_start, date_end, news):

    if date_start != None:
        date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d')
    else:
        date_start = datetime.datetime.strptime('1990-01-01', '%Y-%m-%d')

    if date_end != None:
        datetime.datetime.strptime(date_end,'%Y-%m-%d')
    else:
        date_end = datetime.datetime.today().strftime('%Y-%m-%d')

    result = sgsubmission.find({
        'created_utc': {'gte': date_start, 'lte': date_end},
        'link_flair_text'
    })

client = MongoClient('localhost', 27017)

db = client.Reddit

sgsubmission = db['submission']
sgcomment = db['comments']

