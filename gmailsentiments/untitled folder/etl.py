from codecs import utf_16_be_decode
import dataclasses
from tkinter import scrolledtext
import pymongo
import time
from sqlalchemy import create_engine
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

analyser = SentimentIntensityAnalyzer()

# Establish a connection to the MongoDB server
client = pymongo.MongoClient(host="mongodb", port=27017)

time.sleep(10)  # seconds

# Select the database you want to use withing the MongoDB server
db = client.gmail

pg = create_engine('postgresql://joric:0809@postgresdb:5432/gmail', echo=True)

#mentions_regex= '[A-Za-z0-9_]+'
url_regex='https?:\/\/\S+' #this will not catch all possible URLs
hashtag_regex= '#'
rt_regex= 'RT\s'
utf_regex= re.compile(u'('u'\ud83c[\udf00-\udfff]|'u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'u'[\u2600-\u26FF\u2700-\u27BF])+', re.UNICODE)
white_sp = r'[^\w|@]'


def clean_messages(message):
    #message = re.sub(mentions_regex, '', message)  #removes @mentions
    message = re.sub(hashtag_regex, '', message) #removes hashtag symbol
    message = re.sub(url_regex, '', message) #removes most URLs
    message = re.sub(utf_regex, '', message) #removes utf emojis 
    message = re.sub(white_sp, ' ', message) # removes all non-alphanumeric except : - @
    return message





#while True:
docs = list(db.messages.find())
for doc in docs:   
    date = doc['Date']
    subject = clean_messages(doc['Subject'])
    sender = clean_messages(doc['Sender'])
    snippet = clean_messages(doc['Snippet'])
    data={'date':[date], 'subject':[subject], 'sender':[sender] , 'snippet':[snippet]}
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    
    for data in pd.DataFrame(df):
        Snippet = df['snippet']
        sentiment = analyser.polarity_scores(Snippet)['compound']  # placeholder value
        df['sentiment']= sentiment
    df.to_sql('messages',con = pg, index=False, if_exists='append')
    #time.sleep(5)
