"""
-------------------------------------------------------------------
-- Project: Analysis of Coronavirus related Tweets using TwitterAPI
-- Author:  Georgios Spyrou
-- Last Updated:  09/09/2020
-------------------------------------------------------------------
"""

import os
import argparse
import json
from datetime  import datetime, timedelta

# Twitter API
from searchtweets import load_credentials
from searchtweets import gen_rule_payload
from searchtweets import ResultStream


# Secure location of the required keys to connect to the API
# This config also contains the search query
json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    config = json.load(json_file)

# Project folder location and keys
os.chdir(config["project_directory"])

# Import the custom functions that we will use to retrieve and analyse
# the data, and use the API to save the data to a .jsonl file.

import twitter_custom_functions as tcf

keys_yaml_location = config["keys"]

# Load the credentials to get access to the API
premium_search_args = load_credentials(filename=keys_yaml_location,
                                       yaml_key="search_tweets_api_fullarchive",
                                       env_overwrite=False)
print(premium_search_args)

# Set tweet extraction period and create a list of days of interest

parser=argparse.ArgumentParser()
parser.add_argument('fromDate', type=str)
parser.add_argument('toDate', type=str)
args = parser.parse_args()

if args.toDate <= args.fromDate:
    print('The date range given is invalid. Please give correct from/to dates')
    exit()

daysList = [args.fromDate]

print(f'Collecting Tweets from: {args.fromDate} to {args.toDate}')

while args.fromDate != args.toDate:
    date = datetime.strptime(args.fromDate, "%Y-%m-%d")
    mod_date = date + timedelta(days=1)
    incrementedDay = datetime.strftime(mod_date, "%Y-%m-%d")
    daysList.append(incrementedDay)
    
    args.fromDate = incrementedDay
    

# Retrieve the data for each day from the API
for day in daysList:
    
    dayNhourList = tcf.create_date_time_frame(day, hourSep=2)
    
    for hs in dayNhourList:
        fromDate = hs[0]
        toDate = hs[1]
        # Create the searching rule for the stream
        rule = gen_rule_payload(pt_rule=config['search_query'],
                                from_date=fromDate,
                                to_date=toDate ,
                                results_per_call=100)

        # Set up the stream
        rs = ResultStream(rule_payload=rule, max_results=100,
                          **premium_search_args)

        # Create a .jsonl with the results of the Stream query
        #file_date = datetime.now().strftime('%Y_%m_%d_%H_%M')
        file_date = '_'.join(hs).replace(' ', '').replace(':','')
        filename = os.path.join(config["outputFiles"],
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
