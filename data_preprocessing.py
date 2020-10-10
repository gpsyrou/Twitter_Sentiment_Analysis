import pandas as pd
import pickle
import json
import os
import seaborn as sns
from nltk.corpus import stopwords

import sys
sys.path.append('../')

import utilities.twitter_custom_functions as tcf
from sentiment_class import TwitterSentiment

json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    config = json.load(json_file)

# Project folder location and keys
os.chdir(config["project_directory"])

sns.set_style("darkgrid")

all_tweets_list_file_loc = r'all_tweets_list.txt'

with open(all_tweets_list_file_loc, 'rb') as file:
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

print('removing hyperlink finished..')

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

# Remove punctuation and stop words
allStopWords = list(stopwords.words('english'))
spanish_stopwords = list(stopwords.words('spanish'))

# Remove common words or punctuation used in tweets plus the term that we
# used for the query
commonTwitterStopwords = ['rt', 'RT', 'retweet', 'new', 'via', 'us', 'u',
                          'covid', 'coronavirus', '2019', 'coronavírus',
                          '#coronavirus', '19', '#covid', '#covid19',
                          '#covid2019', '…', '...', '“', '”', '‘', '’']

allStopWords.extend(commonTwitterStopwords + spanish_stopwords)
num_list = '0123456789'

tweets_df['Tweets_Clean'] = tweets_df['Tweet_Translated'].apply(
        lambda x: tcf.remove_punct_and_stopwords(x, allStopWords, num_list))

tweets_df = tweets_df[tweets_df['Tweets_Clean'].notnull()].reset_index()

# Save the data
tweets_df.to_csv(translated_tweets_filename, sep='\t', encoding='utf-8',
                 index=False)

print('File created in: {0}'.format(os.path.join(os.getcwd(), translated_tweets_filename)))
