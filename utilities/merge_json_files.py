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
json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    config = json.load(json_file)

os.chdir(config["project_directory"])

import twitter_custom_functions as tcf

# Read the data from the jsonl files
jsonl_files_folder = os.path.join(config["project_directory"],
                                  config["raw_data_folder"])

all_tweets = []

print('Merging {0} json files...'.format(len(os.listdir(jsonl_files_folder))))

for file in os.listdir(jsonl_files_folder):
    if 'twitter' in file:
        tweet_batch = tcf.load_jsonl_data(os.path.join(jsonl_files_folder,
                                                          file))
        all_tweets += tweet_batch
        
print('Merging completed...')

# Pickle the list to a common .txt file
out_filename = 'all_tweets_list.txt'
with open(out_filename, 'wb') as file:
    pickle.dump(all_tweets, file)

print(f'There are {int(len(all_tweets))} tweets saved in {out_filename}')
