"""
-------------------------------------------------------------------
-- Project: Analysis of Coronavirus related Tweets using TwitterAPI
-- Author:  Georgios Spyrou
-- Last Updated:  10/09/2020
-------------------------------------------------------------------
"""

import os
import json
import pickle

# Secure location of the required keys to connect to the API
# This config also contains the search query (in this case 'coronavirus')
json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    config = json.load(json_file)

# Project folder location and keys
os.chdir(config["project_directory"])

import twitter_custom_functions as tcf

# Read the data from the jsonl files
jsonl_files_folder = os.path.join(config["project_directory"],
                                  config["outputFiles"])

# List that will contain all the Tweets that we managed to receive
# via the use of the API

allTweetsList = []

print('Merging the json files...')

for file in os.listdir(jsonl_files_folder):
    if 'twitter' in file:
        tweets_full_list = tcf.load_jsonl_data(os.path.join(jsonl_files_folder,
                                                          file))
        allTweetsList += tweets_full_list
        
print('Merging completed...')

# Pickle the list to a common .txt file
out_filename = 'all_tweets_list.txt'
with open(out_filename, 'wb') as file:
    pickle.dump(allTweetsList, file)

print(f'The text file has saved {int(len(allTweetsList))} tweets in {out_filename}')
