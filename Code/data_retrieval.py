"""
-------------------------------------------------------------------
-- Title:   Analysis of Coronavirus related Tweets using TwitterAPI
-- File:    data_retrieval.py
-- Purpose: Retrieve data by using the Twitter API
-- Author:  Georgios Spyrou
-- Last Updated:    09/09/2020
-------------------------------------------------------------------
"""

# Data retrival from Twitter API

# Import dependencies
import os
import json
from datetime  import datetime, timedelta

# Twitter API
from searchtweets import load_credentials
from searchtweets import gen_rule_payload
from searchtweets import ResultStream

# Set up the project environment

# Secure location of the required keys to connect to the API
# This config also contains the search query
json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    configFile = json.load(json_file)

# Project folder location and keys
os.chdir(configFile["project_directory"])

keys_yaml_location = configFile["keys"]

# Load the credentials to get access to the API
premium_search_args = load_credentials(filename=keys_yaml_location,
                                       yaml_key="search_tweets_api_30day",
                                       env_overwrite=False)
print(premium_search_args)


# Set tweet extraction period and create a list of days of interest
fromDate = "2020-08-20"
toDate = "2020-08-22"


# Create the searching rule for the stream
rule = gen_rule_payload(pt_rule=configFile['search_query'],
                        from_date=fromDate,
                        to_date=toDate ,
                        results_per_call = 100)

# Set up the stream
rs = ResultStream(rule_payload=rule,
                    max_results=100,
                    **premium_search_args)

# Create a .jsonl with the results of the Stream query
file_date = fromDate + '_' + toDate
filename = os.path.join(configFile["outputFiles"],
                        f'twitter_30day_results_{file_date}.jsonl')
    
# Write the data received from the API to a file
with open(filename, 'a', encoding='utf-8') as f:
    cntr = 0
    for tweet in rs.stream():
        cntr += 1
        if cntr % 100 == 0:
            n_str, cr_date = str(cntr), tweet['created_at']
            print(f'\n {n_str}: {cr_date}')
            json.dump(tweet, f)
            f.write('\n')
print(f'Created file {f}:')
