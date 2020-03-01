"""
-------------------------------------------------------------------
-- Title:   Analysis of Coronavirus related Tweets using TwitterAPI
-- File:    TwitterDataRetrieval.py
-- Purpose: Script used to retrieve the tweets through TwitterAPI.
-- Author:  Georgios Spyrou
-- Date:    01/03/2020
-------------------------------------------------------------------
"""

# Data retrival from Twitter API

# Import dependencies
import os

import json
from datetime  import datetime, timedelta

# Twitter related
from searchtweets import load_credentials
from searchtweets import gen_rule_payload
from searchtweets import ResultStream

# Set up the project environment

# Secure location of the required keys to connect to the API
# This config also contains the search query
json_loc = '/Users/georgiosspyrou/Desktop/config_tweets/Twitter/twitter_config.json'

with open(json_loc) as json_file:
    data = json.load(json_file)

# Project folder location and keys
os.chdir(data["project_directory"])

# Import the custom functions that we will use to retrieve and analyse
# the data, and use the API to save the data to a .jsonl file.

import twitterCustomFunc as twf

twitter_keys_loc = data["keys"]

# Load the credentials to get access to the API
premium_search_args = load_credentials(twitter_keys_loc,
                                       yaml_key="search_tweets_api",
                                       env_overwrite=False)
print(premium_search_args)


# Set tweet extraction period and create a list of days of interest
fromDate = "2020-02-21"
toDate = "2020-02-25"

daysList = [fromDate]

while fromDate != toDate:
    date = datetime.strptime(fromDate, "%Y-%m-%d")
    mod_date = date + timedelta(days=1)
    incrementedDay = datetime.strftime(mod_date, "%Y-%m-%d")
    daysList.append(incrementedDay)
    
    fromDate = incrementedDay

# Retrieve the data for each day from the API
for day in daysList:
    
    dayNhourList = twf.createDateTimeFrame(day, hourSep=2)
    
    for hs in dayNhourList:
        fromDate = hs[0]
        toDate = hs[1]
        # Create the searching rule for the stream
        rule = gen_rule_payload(pt_rule=data['search_query'],
                                from_date=fromDate,
                                to_date=toDate ,
                                results_per_call = 100)

        # Set up the stream
        rs = ResultStream(rule_payload=rule,
                            max_results=100,
                            **premium_search_args)

        # Create a .jsonl with the results of the Stream query
        #file_date = datetime.now().strftime('%Y_%m_%d_%H_%M')
        file_date = '_'.join(hs).replace(' ', '').replace(':','')
        filename = os.path.join(data["outputFiles"],f'twitter_30day_results_{file_date}.jsonl')
    
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
