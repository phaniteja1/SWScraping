import requests
import json
import time
import datetime
import os
from pymongo import MongoClient
from random import randint

url = "https://www.southwest.com/api/air-booking/v1/air-booking/page/air/booking/shopping"

origin_airport_code = "CVG"

destination_airport_code = "SFO"

payload = {
    "originationAirportCode": "CVG",
    "destinationAirportCode": "SFO",
    "returnAirportCode": "",
    "departureDate": "2018-05-27",
    "departureTimeOfDay": "ALL_DAY",
    "returnDate": "2018-05-30",
    "returnTimeOfDay": "ALL_DAY",
    "adultPassengersCount": "1",
    "seniorPassengersCount": "0",
    "fareType": "USD",
    "passengerType": "ADULT",
    "tripType": "roundtrip",
    "promoCode": "",
    "reset": "true",
    "redirectToVision": "true",
    "int": "HOMEQBOMAIR",
    "leapfrogRequest": "true",
    "application": "air-booking",
    "site": "southwest"
}

headers = {
    'x-api-key': "l7xx944d175ea25f4b9c903a583ea82a1c4c",
    'content-type': "application/json",
    'cache-control': "no-cache"
    }

# mongolab params setup
uri = 'mongodb://helloworld:helloworldpassword@ds217310.mlab.com:17310/cheapestflight?authMechanism=SCRAM-SHA-1'
client = MongoClient(uri)
db = client.cheapestflight
collection = db.swdata

def getDataAndWriteToFile():
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers, verify=False)

    print(response.text)
    # create a file name with the current airports, date and time
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    filename = 'prices/' + origin_airport_code + ' - ' + destination_airport_code + ' --- ' + timestamp + '.json'

    file_contents = json.loads(response.text)

    with open(filename, 'w') as outfile:
        json.dump(file_contents, outfile, indent = 4, ensure_ascii = False)

    return (json.loads(response.text))

def saveDataToMongo(data):
	# print(collection)
	# format the data --> adding timestamp to the json object
	ts = time.time()
    	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

	formatted_data = { 'timestamp_of_price_request': timestamp, 'flight_data': data }

	collection.insert_one(formatted_data)
	print('Inserted a document to mongolab', timestamp)

def writeAllFilesToMongo():
	path = 'prices/'
	listing = os.listdir(path)
	for file in listing:
		# print('Current file name : ', file)
		page = open(path + file, 'r')
		parsed_data = json.loads(page.read())

		# get the timestamp from the filename
		filename = os.path.basename(file)
	    	formatted_file_timestamp = os.path.basename(page.name)[-25:-5]

		# format the data to include the timestamp
		formatted_data = { 'timestamp_of_price_request': formatted_file_timestamp, 'flight_data': parsed_data }

		json_data_id = collection.insert_one(formatted_data)
		print('Inserted the document')


while True:
	# writeAllFilesToMongo() # do run this only if you wish to do a bulk insert of all the files to mongolab
	data = getDataAndWriteToFile()
	saveDataToMongo(data)
    	sleep_interval = randint(3000,4200)
    	time.sleep(sleep_interval)
