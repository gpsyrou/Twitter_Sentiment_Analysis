"""
-------------------------------------------------------------------
-- Title:   Analysis of Coronavirus related Tweets using TwitterAPI
-- File:    merge_json_files.py
-- Purpose: Script used to merge the json files into a common txt file
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
    configFile = json.load(json_file)

# Project folder location and keys
os.chdir(configFile["project_directory"])

import twitter_custom_functions as tcf

# Read the data from the jsonl files
jsonl_files_folder = os.path.join(configFile["project_directory"],
                                  configFile["outputFiles"])

# List that will contain all the Tweets that we managed to receive
# via the use of the API

allTweetsList = []

print('Merging the json files...')

for file in os.listdir(jsonl_files_folder):
    if 'twitter' in file:
        tweets_full_list = tcf.loadJsonlData(os.path.join(jsonl_files_folder,
                                                          file))
        allTweetsList += tweets_full_list
        
print('Merging completed...')

# Pickle the list to a common .txt file
with open('all_tweets_list.txt', 'wb') as file:
    pickle.dump(allTweetsList, file)

print(f'The text file has saved {int(len(allTweetsList))} tweets')
