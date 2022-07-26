
import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# Importing required libraries

from apiclient import errors
from httplib2 import Http

import base64
import re
import time
import dateutil.parser as parser
from datetime import datetime
import datetime
import logging
import pymongo
import codecs


# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


user_id =  'me'
label_id_one = 'INBOX'
label_id_two = 'UNREAD'

def search_messages(service):
    unread_msgs = service.users().messages().list(userId='me',labelIds=[label_id_one, label_id_two]).execute()
    return unread_msgs['messages']




def read_message(service):

#for mssg in search_messages(service):
	temp_dict = { }
	m_id = mssg['id'] # get id of individual message
	message = service.users().messages().get(userId=user_id, id=m_id).execute() # fetch the message using API
	payld = message['payload'] # get payload of the message 
	headr = payld['headers'] # get header of the payload
	


	for one in headr: # getting the Subject
		if one['name'] == 'Subject':
			msg_subject = one['value']
			temp_dict['Subject'] = str(msg_subject).strip()
		else:
			pass


	for two in headr: # getting the date
		if two['name'] == 'Date':
			msg_date = two['value']
			date_parse = (parser.parse(msg_date))
			m_date = date_parse.strftime("%Y-%m-%d %H:%M:%S")
			temp_dict['Date'] = str(m_date).strip()
		else:
			pass

	for three in headr: # getting the Sender
		if three['name'] == 'From':
			msg_from = three['value']
			temp_dict['Sender'] = str(msg_from).strip()
		else:
			pass

	temp_dict['Snippet'] = str(message['snippet']).strip() # fetching message snippet
	
	return temp_dict

	


def markasread():
	for mssg in search_messages(service):
		m_id = mssg['id']
		return service.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute() 
		
		

def connect_mongo():
	client_docker = pymongo.MongoClient(host="mongodb", port=27017) # hostname = servicename for docker-compose pipeline
	db = client_docker.gmail
	collection = db.messages
	return collection
	

service = gmail_authenticate()
final_list = [ ]
while True:
	unread = search_messages(service)
	print ("Total unread messages in inbox: ", str(len(unread)))
	for mssg in unread:
		message=read_message(service)
		final_list.append(message)
		markasread()
	
	
	for msg in final_list:
		connect_mongo().insert_one(msg)
		
	time.sleep(3)