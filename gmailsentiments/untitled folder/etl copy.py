from cmath import phase
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
pg.execute('''
    CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP,
    sender TEXT,
    subject TEXT,
    snippet TEXT,
    sentiment NUMERIC
);
''')


#mentions_regex= '[A-Za-z0-9_]+'
url_regex='https?:\/\/\S+' #this will not catch all possible URLs
hashtag_regex= '#'
rt_regex= 'RT\s'
utf_regex= re.compile(u'('u'\ud83c[\udf00-\udfff]|'u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'u'[\u2600-\u26FF\u2700-\u27BF])+', re.UNICODE)
white_sp = r'[^\w|@,.]'


def clean_messages(message):
    #message = re.sub(mentions_regex, '', message)  #removes @mentions
    message = re.sub(hashtag_regex, '', message) #removes hashtag symbol
    message = re.sub(url_regex, '', message) #removes most URLs
    message = re.sub(utf_regex, '', message) #removes utf emojis 
    message = re.sub(white_sp, ' ', message) # removes all non-alphanumeric except : - @
    return message





while True:
    docs = db.messages.find()
    for doc in docs:   
        date = doc['Date']
        subject = doc['Subject']
        sender = doc['Sender']
        snippet = clean_messages(doc['Snippet'])
        data={'date':[date], 'subject':[subject], 'sender':[sender] , 'snippet':[snippet]}
        df = pd.DataFrame.from_dict(data,orient='index')
        print(df.columns)
        date = df['date']
        sender = df['sender']
        subject = df['subject']
        snippet = df['snippet']
        sentiment = analyser.polarity_scores(snippet)['compound']  # placeholder value
        #df['sentiment']= sentiment
        #sentiment = df['sentiment']
        #df.to_sql('messages',con = pg, index=False,if_exists='append')
        #df = pd.DataFrame(df)
        
        query = "INSERT INTO messages VALUES (%s,%s,%s,%s,%s)ON CONFLICT DO NOTHING;"
        pg.execute(query,(date,sender,subject,snippet,sentiment))
    time.sleep(1)
