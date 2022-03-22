#!/bin/bash -x
#Script to run messenger as GUI for a wit.ai chatbot
WIT_TOKEN=$WIT_TOKEN FB_VERIFY_TOKEN=$FB_VERIFY_TOKEN FB_PAGE_TOKEN=$FB_PAGE_TOKEN WIT_API_VERSION=$WIT_API_VERSION python wit_messenger_chatbot_automated_logic.py  $FB_MES_WEBHOOK_PORT

