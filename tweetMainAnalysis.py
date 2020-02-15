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
import json_lines
from datetime  import datetime

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

import twitter_functions as twf

twitter_keys_loc = data["keys"]

# Load the credentials to get access to the API
premium_search_args = load_credentials(twitter_keys_loc,
                                       yaml_key="search_tweets_api",
                                       env_overwrite=False)
print(premium_search_args)

# Create the searching rule for the stream
rule = gen_rule_payload(pt_rule=data['search_query'],
                        from_date="2020-01-01",
                        to_date="2020-02-15" )

# Set up the stream
rs = ResultStream(rule_payload=rule,
                  max_results=3000,
                  **premium_search_args)
print(rs)    


# Create a .jsonl with the results of the Stream query
file_date = datetime.now().strftime('%Y_%m_%d_%H_%M')
filename = os.path.join('C:\\Users\\hz336yw\\Desktop\\',f'twitter_premium_api_results_{file_date}.jsonl')

# Write the data received from the API to a file
with open(filename, 'a', encoding='utf-8') as f:
    cntr = 0
    for tweet in rs.stream():
        cntr += 1
        if cntr % 100 == 0:
            print(f'{str(n)}: {tweet[\'created_at\']}')
        json.dump(tweet, f)
        f.write('\n')


# 3. Import the data from the created .jsonl file

# Read the data from the jsonl file
tweets_full_list = twf.loadJsonlData(filename)

# 4. Main exploratory data analysis on the data received from the API.

# Create a dataframe based on the relevant data from tweets_full_list
user_ls = []
tweet_ls = []
location_ls = []
datetime_ls = []

for tweet_dict in tweets_full_list:
    user_ls.append(tweet_dict['user']['screen_name'])
    tweet_ls.append(twf.removeURL(tweet_dict['text']))
    location_ls.append(tweet_dict['user']['location'])
    datetime_ls.append(tweet_dict['created_at'])
    
# Dataframe that contains the data for analysis
# Note: The twitter API functionality is very broad in what data we can analyse
# This project will focus on tweets and with their respective location/date.
df = pd.DataFrame(list(zip(user_ls, tweet_ls, location_ls, datetime_ls)), 
                  columns = ['Username','Tweet','Location', 'Date'])



# Remove punctuation and stop words
from nltk.corpus import stopwords

eng_stopwords = set(stopwords.words('english'))
num_list = '0123456789'

df['Tweet'] = df['Tweet'].apply(lambda x: 
    twf.rmPunctAndStopwords(x, eng_stopwords, num_list))


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
