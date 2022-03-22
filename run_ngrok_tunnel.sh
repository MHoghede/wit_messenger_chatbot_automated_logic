#!/bin/bash
#Usage:
#When running a free service for ngrok:
#./run_ngrok_tunnel.sh
#When you have a PAID BASIC plan ngrok:
#./run_ngrok_tunnel.sh <somesubdomainofchoice>
#Substitute <somesubdomainofchoice>
#with your preferred ngrok.io subdomain
#Uncomment below line when running a free service
ngrok http 8445
#Uncomment below line when running the basic PAID plan
#ngrok http -subdomain=$1 8445
