"""
-------------------------------------------------------------------
-- Title:   Main Analysis of Coronavirus related Tweets retrieved via the TwitterAPI
-- File:    main.py
-- Purpose: Main script which contains the analysis regarding the tweets.
-- Author:  Georgios Spyrou
-- Last Updated:    10/09/2020
-------------------------------------------------------------------
"""

import pandas as pd
import pickle
import json
import os

# Plots and graphs
import seaborn as sns

# NLTK module for text preprocessing and analysis
from nltk.corpus import stopwords

json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    configFile = json.load(json_file)

# Project folder location and keys
os.chdir(configFile["project_directory"])

import utilities.twitter_custom_functions as tcf
import Code.plot_world_map as pmap
from Code.sentiment_class import TwitterSentimentDataframe

sns.set_style("darkgrid")

all_tweets_list_file_loc = r'all_tweets_list.txt'

with open (all_tweets_list_file_loc, 'rb') as file:
    allTweetsList = pickle.load(file)


# Create a dataframe based on the relevant data from the full list of the 
# received tweets
user_ls, userid_ls, tweet_ls = [], [], []
location_ls, datetime_ls, replyto_ls = [], [], []
geo_loc_ls = []

for tweet_dict in allTweetsList:
    user_ls.append(tweet_dict['user']['screen_name'])
    userid_ls.append(tweet_dict['user']['id'])
    tweet_ls.append(tcf.remove_url(tweet_dict['text']))
    replyto_ls.append(tweet_dict['in_reply_to_user_id'])
    location_ls.append(tweet_dict['user']['location'])
    datetime_ls.append(tweet_dict['created_at'])

# Dataframe that contains the data for analysis
# Note: The twitter API functionality is very broad in what data we can analyse
# This project will focus on tweets and with their respective location/date.
tweets_df = pd.DataFrame(list(zip(user_ls, userid_ls, tweet_ls,
                           replyto_ls, location_ls, datetime_ls)),
                  columns=['Username', 'UserID', 'Tweet', 'Reply_to',
                           'Location', 'Date'])

# Remove tweets that they did not have any text
tweets_df = tweets_df[tweets_df['Tweet'].notnull()].reset_index()
tweets_df.drop(columns=['index'], inplace=True)

# Add Year and Month columns corresponding to each tweet
tweets_df['Year'] = pd.DatetimeIndex(tweets_df['Date']).year
tweets_df['Month'] = pd.DatetimeIndex(tweets_df['Date']).month

# Detect language and translate if necessary
translated_tweets_filename = 'tweets_translated.csv'

tweets_df['Tweet_Translated'] = tweets_df['Tweet'].apply(lambda text:
                                                    tcf.translate_tweet(text))

tweets_df.to_csv(translated_tweets_filename, sep='\t', encoding='utf-8',
                 index=False)



# Import the latest version of the csv that holds the translated data
tweets_df = pd.read_csv(translated_tweets_filename, sep='\t',
                        encoding = 'utf-8', index_col=None)



'''
# Unfortunately TwitterAPI doesn't give much information regarding coordinates.
# But we can try to find the geolocation (long/lat) through the use of geopy
# Geopy has a limit in the times we can call it per second so we have to find
# a workaround

geolocator = Nominatim(user_agent="https://developer.twitter.com/en/apps/17403833") 
   
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1,
                      max_retries=3, error_wait_seconds=2)

# Split it in batches and identify the locations
step = 100

for batch in range(0, tweets_df.shape[0], step):
    batchstep = batch+step
    if batchstep > tweets_df.shape[0]:
        batchstep = batch + (tweets_df.shape[0]%step)
    print(f'\nCalculating batch: {batch}-{batchstep}\n')
    tweets_df['Point'] = tweets_df['Location'][batch:batchstep].apply(lambda x:
        tcf.get_valid_coordinates(x, geolocator))

dfWithCoords = tweets_df[tweets_df['Point'].notnull()]
dfWithCoords['Latitude'] = dfWithCoords['Point'].apply(lambda x: x[0])
dfWithCoords['Longitude'] = dfWithCoords['Point'].apply(lambda x: x[1])

fig = pmap.create_tweet_worldmap(dfWithCoords)
plot(fig)

'''

# Remove punctuation and stop words
allStopWords = list(stopwords.words('english'))
spanish_stopwords = list(stopwords.words('spanish'))

# Remove common words or punctuation used in tweets plus the term that we
# used for the query
commonTwitterStopwords = ['rt', 'RT', 'retweet', 'new', 'via', 'us', 'u',
                          'covid','coronavirus', '2019', 'coronavírus',
                          '#coronavirus', '19', '#covid', '#covid19',
                          '#covid2019', '…', '...', '“', '”', '‘', '’']

allStopWords.extend(commonTwitterStopwords + spanish_stopwords)
num_list = '0123456789'

tweets_df['Tweets_Clean'] = tweets_df['Tweet_Translated'].apply(
        lambda x: tcf.remove_punct_and_stopwords(x, allStopWords, num_list))

tweets_df = tweets_df[tweets_df['Tweets_Clean'].notnull()].reset_index()

# 1. Visualize the most common words across all tweets


# All
tweets_all_months = TwitterSentimentDataframe(input_df=tweets_df,
                                              tweet_column='Tweets_Clean')
tweets_all_months.plot_most_common_words(figsize=(10, 8))

# August
tweets_august = TwitterSentimentDataframe(input_df=tweets_df,
                                              tweet_column='Tweets_Clean')
tweets_august.subset_dataframe(year=2020, month=8)

tweets_august.plot_most_common_words(figsize=(10, 8))


# 2. WordCloud vizualisation

# All
tweets_all_months.plot_wordcloud(figsize=(10, 8))
# August
tweets_august.plot_wordcloud(figsize=(10, 8))


# 3. Find bigrams (pairs of words that frequently appear next to each other)
# All
bigrams_all = tweets_all_months.compute_bigrams()
tweets_all_months.plot_bigrams(top_n=20, figsize=(10, 8))

# August
bigrams_august = tweets_august.compute_bigrams()
tweets_august.plot_bigrams(top_n=20, figsize=(10, 8))


# 4. Sentiment analysis on tweets based on Liu Hu opinion lexicon
# Classify tweets as 'positive', 'negative' or 'neutral' based on the polarity
# of the words present in a sentence.
sentimentDF = august_df.copy()

sentimentDF['Sentiment'] = august_df['Tweets_Clean'].apply(lambda tweet:
                                                      tcf.liu_hu_opinion_lexicon(tweet))

# Vizualise the results
tcf.plot_sentiment(input_df=sentimentDF, sentiment_col='Sentiment')
