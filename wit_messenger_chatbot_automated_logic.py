
#!/usr/bin/env python
# coding:utf-8

#
#This is a simple chatbot for answering questions starting with your wit.ai chatbot of choice.
#It uses the pywit library found at
#
#https://github.com/wit-ai/pywit
#
#It is really very generically written, only assuming that you have already preprocessed
#your wit.ai chatbot, as the json files included in the directory:
#
#wit_ai_chatbot_unzipped_dirs
#
#using the command:
#
#python wit_ai_chatbot_db.py 
#
#This produces a file in csv format:
#
#wit_ai_chatbot_db.csv
#
#that could e.g. be read and edited using
#
# Excel of Office Suite
#
#or using
#
#Calc application of  respectively Libre Office or Open Office Suites.
#
#For this  program to work, you then need to copy this file to its new name
#
#wit_ai_chatbot_db.w_answers.csv
#
#and edit this file to supply the answers in the "answer" column.
#
#It is wise to first write protect the other columns, especially as
#this program as yet does not have very good error reporting.
#
#As perhaps expected, the content under directory wit_ai_chatbot_unzipped_dirs
#is what you get by unzipping the saved zip file of your wit.ai chatbot
#and renaming the main directory to wit_ai_chatbot_unzipped_dirs
#(done from within settings menu of chatbot)
#
# We assume you have:
#
# * a Wit.ai bot setup (https://wit.ai/docs/quickstart)
# * a Messenger Platform setup (https://developers.facebook.com/docs/messenger-platform/quickstart)
#
# You need to `pip install the following dependencies: requests, bottle and possibly other packages not included in default installation.
#
# 1. pip install requests bottle wit
# 2a. You can run this example on a cloud service provider like Heroku, Google Cloud Platform or AWS.
#    Note that webhooks must have a valid SSL certificate, signed by a certificate authority and won't work on your localhost unless this is true.
#    It is possible to use Letsencrypt's certbot to get a valid certificate from Letsencrypt if running on your own local host.
#   You could also run this on ngrok and they would supply you with a valid SSL Certificate for the temporary domain(s) you get each time you
#   run an ngrok tunnel (assuming you use the free version of this service).
#
# 2b.  You need to establish the  ngrok tunnel using enclosed script below: 
#
#  ./run_ngrok_tunnel.sh
#        Remark: Keep the script running, it does not need to be restarted everytime the python program is restarted.
#
# 3. Note down  your different tokens for wit.ai site, fb messenger page & fb messenger verification that is  
#    <WIT_TKN>, <PG_TKN> and <VER_TKN> below. 
#    <VER_TKN> could be selected by you yourself and fed into the call to python program and into the application page,
#    done in step 5 below, note that when "correctly" done this step need only to be done once.
#
# 4. Run this python script as a  server e.g. calling the enclosed script as below:
#      WIT_TOKEN=<WIT_TKN> FB_VERIFY_TOKEN=<VER_TKN> FB_PAGE_TOKEN=<PG_TKN> FB_MES_WEBHOOK_PORT=8445 WIT_API_VERSION=20200513  feedo_messenger.sh
#     (Check contents of that script to see how this python program is called directly.)
#
# 5. The first time you are running your python program with a ngrok tunnel,
#     subscribe your page to the Webhooks using <VER_TKN> and `https://<YOUR_HOST>/webhook` as callback URL.
#     using the web page for your Messenger App. You also need to specify FB_VERIFY_TOKEN for the Messenger web hook
#     for this, it could be chosen to not change its value to avoid respecifying at every restart of the python program above
#
#    Do this on the web page for <Messenger App> - Messenger - Facebook for Developers under:
#
#    https://developers.facebook.com/apps/<Messenger App ID>/messenger/settings/
#    Remark:
#             When using a free ngrok tunnel you will get a new host domain (<YOUR_HOST> above) every time, so you need to check the new domain
#              for https / SSL using their web page:
#
#              https://dashboard.ngrok.com/cloud-edge/status
#
#             (You need to be logged in with ngrok for this of course)
#             It is also echoed to the output at least when running a Linux bash script with bash -x.
#
# 6. Talk to your bot on Messenger!

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import requests
from sys import argv
from wit import Wit
from bottle import Bottle, request, debug
import csv

# Wit.ai parameters
WIT_TOKEN = os.environ.get('WIT_TOKEN')
# Messenger API parameters
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')

# Setup Bottle Server
debug(True)
app = Bottle()


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if verify_token == FB_VERIFY_TOKEN:
        # respond with the challenge to confirm
        challenge = request.query.get('hub.challenge')
        return challenge
    else:
        return 'Invalid Request or Verification Token'


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            messages = entry['messaging']
            if messages[0]:
                # Get the first message
                message = messages[0]
                # Yay! We got a new message!
                # We retrieve the Facebook user ID of the sender
                fb_id = message['sender']['id']
                # We retrieve the message content
                text = message['message']['text']
                # Let's forward the message to Wit /message
                # and customize our response to the message in handle_message
                response = client.message(msg=text)
                handle_message(response=response, fb_id=fb_id)
    else:
        # Returned another event
        return 'Received Different Event'
    return None


def send_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content


def find_entity(entities, entity):
    if entity in entities:
        if entities[entity]:
            return True
    return False

def first_intent_value(intents):
    """
    Returns first intent value
    """
    if len(intents):
        name=intents[0]['name']
        if name:
            return name
    return False


def could_not_understand_question(fb_id):
    send_message(fb_id, "Jag förstod inte riktigt. Kan du omformulera frågan?") 

def handle_entities_and_answer_question(fb_id,entities,N,all_entities,my_answer):
    all_entities_found=True
    for k in range(N):
        if not find_entity(entities,all_entities[k]):
            all_entities_found=False
            break
        
    if all_entities_found:
        send_message(fb_id, my_answer)
    return all_entities_found

def handle_message(response, fb_id):
    """
    Customizes our response to the message and sends it
    """

    
    intents=response['intents']
    my_read_intent_name=first_intent_value(intents)
    entities=response['entities']

    all_entities_found=False
    
    with open('wit_ai_chatbot_db.w_answers.csv',"r") as my_chatbot_db_file:
        csv_reader= csv.reader(my_chatbot_db_file)

        next(csv_reader)

        for column in csv_reader:
            my_intent_name=column[0]
            number_of_entities=int(column[1])
            all_entities=[]
            for k in range(number_of_entities):
                all_entities.append(column[2+k])

            my_answer=column[-1]
        
            if my_read_intent_name == my_intent_name:
                all_entities_found=handle_entities_and_answer_question(fb_id,entities,number_of_entities,all_entities,my_answer)
            if all_entities_found:
                break

    if not all_entities_found:
        could_not_understand_question(fb_id)

# Setup Wit Client
client = Wit(access_token=WIT_TOKEN)

if __name__ == '__main__':
    # Run Server
    app.run(host='0.0.0.0', port=argv[1])
