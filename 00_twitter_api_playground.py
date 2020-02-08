# Import dependencies
import os
import tweepy as tw
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import networkx as nx

import json


# Project directory location
os.chdir('C:\\Users\\hz336yw\\Desktop\\Twitter_Project')

# Set up the configuration to the Twitter API
consumer_key = 'pGSgo0UFXiEESa0vt7zTMtiP2'
consumer_secret = 'UWxjYxj470RoYXldF11OlQQT4XEf4RIqhwDHeQSkHLUOlQkOGH'
access_token = '1034131506615267334-LxNsWHtFf44l5wBbtH7uQ3XV18ruWi'
access_token_secret = 'Swt3ghPjqgGPAM62G5H152KF2QL0mdZxa7dksGAZDimrg'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


'''
Fetching the last 20 tweets from FC Barcelona twitter account:

last_20_tweets_of_FC_Barcelona = api.user_timeline('FCBarcelona')
'''


# Search term for the analysis
term_search = "coronavirus -filter:retweets"


tweets = tw.Cursor(api.search, q=term_search, lang='en', exclude_replies=True).items(200)

# This will create a list of json objects with all the info for the tweets
all_tweets_dict = []
for tweet in tweets:
    all_tweets_dict.append(tweet._json)

# Write the results to a text file for future reference
filename = 'all_tweets_20200207.txt'

with open(filename ,'w') as file:
    file.write(json.dumps(all_tweets_dict, indent=4))

import twitter_functions as twf

# Collect the data of interest from the json entries
# and clean the Tweets
with open(filename, encoding='utf-8') as json_file:
    
    user_ls = []
    tweet_ls = []
    location_ls = []
    datetime_ls = []
    
    dataset = json.load(json_file)
    #create a dataframe from the data
    for tweet_dict in dataset:
        user_ls.append(tweet_dict['user']['screen_name'])
        tweet_ls.append(twf.removeURL(tweet_dict['text']))
        location_ls.append(tweet_dict['user']['location'])
        datetime_ls.append(tweet_dict['created_at'])
        
# Dataframe that contains the data for analysis
df = pd.DataFrame(list(zip(user_ls, tweet_ls, location_ls, datetime_ls)), 
                  columns = ['Username','Tweet','Location', 'Date'])


# Remove punctuation and stop words
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import string

eng_stopwords = set(stopwords.words('english'))
num_list = '0123456789'

df['Tweet'] = df['Tweet'].apply(lambda x: twf.rmPunctAndStopwords(x, eng_stopwords, num_list))


# Find the most common words across all tweets
from collections import Counter

tweet_list = list([x.split() for x in df['Tweet'] if x is not None])
all_words_counter = Counter(x for xs in tweet_list for x in set(xs))
all_words_counter.most_common(20)

mostCommontweets= pd.DataFrame(all_words_counter.most_common(20),
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






