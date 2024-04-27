#Imports
import requests
import os
from dotenv import load_dotenv
#Defining constants
load_dotenv() 
API_KEY = os.getenv("API_KEY")
QRN_URL = "https://api.quantumnumbers.anu.edu.au/"

#Functions
'''
Calls remote API to get a Quatnum Random Number
'''
def get_random_number(QRN_URL, API_KEY):
	DTYPE = "hex16"  # uint8, uint16, hex8, hex16
	LENGTH = 1  # between 1--1024
	BLOCKSIZE = 10  # between 1--10. Only needed for hex8 and hex16

	params = {"length": LENGTH, "type": DTYPE, "size": BLOCKSIZE}
	headers = {"x-api-key": API_KEY}

	response = requests.get(QRN_URL, headers=headers, params=params)

	articles = ""
	if response.status_code == 200:
		articles = response.json()
	else:
		print(f"Error: {response.status_code}")
	backer = articles['data'][0]

	return response, int(backer, 16)


#Preparation

#Algorithm