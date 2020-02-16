"""
-------------------------------------------------------------------
-- Title:   Analysis of Coronavirus related Tweets using TwitterAPI
-- File:    tweetMainAnalysis.py
-- Purpose: Main script which contains the analysis regarding the tweets.
-- Author:  Georgios Spyrou
-- Date:    15/02/2020
-------------------------------------------------------------------
"""

# Import dependencies
import os
import pandas as pd
import numpy as np

# Plots and graphs
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

import json
from datetime  import datetime, timedelta

# Twitter related
import tweepy as tw
from searchtweets import load_credentials
from searchtweets import gen_rule_payload
from searchtweets import ResultStream

# 1. Set up the project environment

# Secure location of the required keys to connect to the API
# This config also contains the search query
json_loc = 'C:\\Users\\hz336yw\\Desktop\\Twitter\\twitter_config.json'

with open(json_loc) as json_file:
    data = json.load(json_file)

# Project folder location and keys
os.chdir(data["project_directory"])

# 2. Import the custom functions that we will use to retrieve and analyse
#    the data, and use the API to save the data to a .jsonl file.

import twitterCustomFunc as twf

twitter_keys_loc = data["keys"]

# Load the credentials to get access to the API
premium_search_args = load_credentials(twitter_keys_loc,
                                       yaml_key="search_tweets_api",
                                       env_overwrite=False)
print(premium_search_args)


# Set tweet extraction period and create a list of days of interest
fromDate = "2020-02-02"
toDate = "2020-02-15"

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

# 3. Import the data from the created .jsonl file

# Read the data from the jsonl files
jsonl_files_folder = os.path.join(data["project_directory"],data["outputFiles"])

# List that will contain all the Tweets that we managed to receive
# via the use of the API

allTweetsList = []

for file in os.listdir(jsonl_files_folder):
    tweets_full_list = twf.loadJsonlData(os.path.join(jsonl_files_folder,file))
    allTweetsList += tweets_full_list


############# Data Retrieval - end ##########################



# 4. Main exploratory data analysis on the data received from the API.

# Create a dataframe based on the relevant data from tweets_full_list
user_ls, tweet_ls = [], []
location_ls, datetime_ls = [], []

for tweet_dict in allTweetsList:
    user_ls.append(tweet_dict['user']['screen_name'])
    tweet_ls.append(twf.removeURL(tweet_dict['text']))
    location_ls.append(tweet_dict['user']['location'])
    datetime_ls.append(tweet_dict['created_at'])
    
# Dataframe that contains the data for analysis
# Note: The twitter API functionality is very broad in what data we can analyse
# This project will focus on tweets and with their respective location/date.
df = pd.DataFrame(list(zip(user_ls, tweet_ls, location_ls, datetime_ls)), 
                  columns = ['Username','Tweet','Location', 'Date'])


# Remove tweets that they did not have any text
df = df[df['Tweet'].notnull()]

# Remove punctuation and stop words
from nltk.corpus import stopwords

allStopWords = list(stopwords.words('english'))
spanish_stopwords = list(stopwords.words('spanish'))

# Remove common words used in tweets plus the term that we used for the query
commonTweeterStopwords = ['rt','retweet','#{0}'.format(data['search_query'])]
                          
allStopWords.extend(commonTweeterStopwords + spanish_stopwords)
num_list = '0123456789'

df['Tweet'] = df['Tweet'].apply(lambda x: 
    twf.rmPunctAndStopwords(x, allStopWords, num_list))


# Find the most common words across all tweets
from collections import Counter

tweet_list = list([x.split() for x in df['Tweet'] if x is not None])
all_words_counter = Counter(x for xs in tweet_list for x in set(xs))
all_words_counter.most_common(20)

mostCommontweets= pd.DataFrame(all_words_counter.most_common(30),
                             columns=['words', 'count'])
mostCommontweets.head()

# Some visualizations

# 1. Visualize the most common words across all tweets
twf.plotMostCommonWords(mostCommontweets)


# 2. WordCloud viz
from wordcloud import WordCloud

plt.figure(figsize=(10,10))
gen_text = ' '.join([x for x in df['Tweet'] if x is not None])
wordcloud = WordCloud().generate(gen_text)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

# Find bigrams