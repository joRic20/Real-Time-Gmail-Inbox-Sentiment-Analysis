
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
		build('gmail', 'v1', credentials=creds)
# get the Gmail API service
service = build('gmail', 'v1', credentials=creds)


user_id =  'me'
label_id_one = 'INBOX'
label_id_two = 'UNREAD'

# Getting all the unread messages from Inbox
# labelIds can be changed accordingly
unread_msgs = service.users().messages().list(userId='me',labelIds=[label_id_one, label_id_two],).execute()

# We get a dictonary. Now reading values for the key 'messages'
mssg_list = unread_msgs['messages']


print ("Total unread messages in inbox: ", str(len(mssg_list)))

final_list = [ ]

while True:
	for mssg in mssg_list:
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
		
		'''try:
			
			# Fetching message body
			mssg_parts = payld['parts'] # fetching the message parts
			part_one  = mssg_parts[0] # fetching first element of the part 
			part_body = part_one['body'] # fetching body of the message
			part_data = part_body['data'] # fetching data from the body
			clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
			clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
			clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
			soup = BeautifulSoup(clean_two , "lxml" )
			mssg_body = soup.body()
			# mssg_body is a readible form of message body
			# depending on the end user's requirements, it can be further cleaned 
			# using regex, beautiful soup, or any other method
			#temp_dict['Message_body'] = mssg_body

		except :
			pass'''

		print (temp_dict)
		final_list.append(temp_dict) # This will create a dictonary item in the final list
		
		# This will mark the messagea as read
		service.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute() 
		
		
	
	# Create a connection to the MongoDB database server
	client_docker = pymongo.MongoClient(host="mongodb", port=27017) # hostname = servicename for docker-compose pipeline

	# Create/use a database
	db = client_docker.gmail
	# equivalent of CREATE DATABASE twitter;

	# Define the collection
	collection = db.messages
	# equivalent of CREATE TABLE tweets





	print ("Total messaged retrived: ", str(len(final_list)))


	#exporting the values as .csv


	# Insert the tweet into the collection
	for msg in final_list:
		collection.insert_one(msg) #equivalent of INSERT INTO tweet_data VALUES (....);
		

	time.sleep(3)
 