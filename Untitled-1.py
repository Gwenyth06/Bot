import tweepy
import firebase_admin
import requests
import re
import os
import schedule
import random
import time
import json
from bs4 import BeautifulSoup
from firebase_admin import db

api_key = ""
api_secret = ""
bearer_token = r""
access_token = ""
access_token_secret = ""

client = tweepy.Client(bearer_token,api_key,api_secret,access_token,access_token_secret)

auth = tweepy.OAuth1UserHandler(api_key,api_secret,access_token,access_token_secret)
api = tweepy.API(auth)

cred_obj = firebase_admin.credentials.Certificate(r'')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL': ""
	})

def file_exists(file_path):
    if( not os.path.exists(file_path)):
        file_name = "medic_voicelines.json"

        with open(file_name, "w") as json_file:
            print("File has been created.")
            pass
    else:
        print("File already exists.")
        
def is_file_empty(file_path):
    if( os.path.getsize(file_path) == 0):
        URL = "https://wiki.teamfortress.com/wiki/Medic_responses"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")

        for a_tag in soup.find_all("a",class_="internal"):
            for b_tag in a_tag.find_all("b"):
                b_tag.decompose()


        counter = 0

        voicelines_dict = {}

        for a_tag in soup.find_all("a", class_="internal"):
            counter += 1 
            lines = a_tag.get_text()
            cleaned_lines = re.sub(r'\([^)]*\)', '', lines)
            cleaned_lines = re.sub(r'\[[^\]]*\]', '', cleaned_lines)
            matched_lines = re.findall(r'"([^"]*)"', cleaned_lines)
            for matches in matched_lines:
                text = matches
                key = counter
                voicelines_dict[key] = text 
                print(matches.strip())

        with open('medic_voicelines.json', 'w') as json_file:
            json.dump(voicelines_dict, json_file, indent=4)

        print("counter: {}".format(counter))

        ref = db.reference("/")

        with open("medic_voicelines.json", "r") as f:
            file_contents = json.load(f)
            ref.set(file_contents)
    else:
        print("File is not empty.")

def is_database_empty():
    ref = db.reference("/")
    data = ref.get()
    if data is None:
        print("Database is empty, uploading voice lines...")
        file_path = r""
        file_exists(file_path)
        is_file_empty(file_path)
        print("Uploading succesfull.")
        return True
    else:
        print("Database is not empty.")
        return False
    
def post():
    ref = db.reference("/")
    voiceline_dict_data = ref.get()

    if voiceline_dict_data:
        random_indices = random.sample(range(len(voiceline_dict_data)),min(len(voiceline_dict_data), 2))
        for index in random_indices:
            line = voiceline_dict_data[index]
            client.create_tweet(text = line)


if(not is_database_empty()):
    schedule.every().day.at("00:00").do(post)

while True:
    schedule.run_pending()
    time.sleep(1)

