"""
-------------------------------------------------------------------
-- Title:   Main Analysis of Coronavirus related Tweets retrieved via the TwitterAPI
-- File:    main.py
-- Purpose: Main script which contains the analysis regarding the tweets.
-- Author:  Georgios Spyrou
-- Last Updated:    10/09/2020
-------------------------------------------------------------------
"""

# Import dependenciescle
import pandas as pd
import pickle
import json
import os

from collections import Counter
from datetime import datetime

# Plots and graphs
import matplotlib.pyplot as plt
import seaborn as sns

from wordcloud import WordCloud
from plotly.offline import plot

# NLTK module for text preprocessing and analysis
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from nltk.corpus import stopwords
from nltk import word_tokenize

# Location API
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    configFile = json.load(json_file)

# Project folder location and keys
os.chdir(configFile["project_directory"])

import Code.twitter_custom_functions as tcf
import Code.plotWorldMap as pmap


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
    tweet_ls.append(tcf.removeURL(tweet_dict['text']))
    replyto_ls.append(tweet_dict['in_reply_to_user_id'])
    location_ls.append(tweet_dict['user']['location'])
    datetime_ls.append(tweet_dict['created_at'])
    geo_loc_ls.append(tweet_dict['geo'])

# Dataframe that contains the data for analysis
# Note: The twitter API functionality is very broad in what data we can analyse
# This project will focus on tweets and with their respective location/date.
tweets_df = pd.DataFrame(list(zip(user_ls, userid_ls, tweet_ls,
                           replyto_ls, location_ls, datetime_ls, geo_loc_ls)),
                  columns=['Username', 'UserID', 'Tweet',
                           'Reply_to', 'Location', 'Date', 'Coordinates'])

# Remove tweets that they did not have any text
tweets_df = tweets_df[tweets_df['Tweet'].notnull()].reset_index()
tweets_df.drop(columns=['index'], inplace=True)


# Detect language and translate if necessary
tweets_df['Tweet_Translated'] = tweets_df['Tweet'].apply(lambda text: tcf.translateTweet(text))

translated_filename = 'tweets_translated_{0}.csv'.format(datetime.today().strftime('%Y-%m-%d'))
tweets_df.to_csv(translated_filename, sep='\t', encoding='utf-8', index=False)


''' Use the below to avoid re-translating
tweets_df.to_csv('full_tweets_20200912.csv', sep='\t', encoding='utf-8', index=False)

tweets_df = pd.read_csv(translated_filename, sep='\t', encoding = 'utf-8', index_col=None)
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
        tcf.getValidCoordinates(x, geolocator))

dfWithCoords = tweets_df[tweets_df['Point'].notnull()]
dfWithCoords['Latitude'] = dfWithCoords['Point'].apply(lambda x: x[0])
dfWithCoords['Longitude'] = dfWithCoords['Point'].apply(lambda x: x[1])

fig = pmap.createTweetWorldMap(dfWithCoords)
plot(fig)



# Remove punctuation and stop words
allStopWords = list(stopwords.words('english'))
spanish_stopwords = list(stopwords.words('spanish'))

# Remove common words used in tweets plus the term that we used for the query
commonTweeterStopwords = ['rt', 'retweet', 'new', 'via', 'us', 'u', '2019',
                          'coronavírus','coronavirus','#coronavirus' ]

allStopWords.extend(commonTweeterStopwords + spanish_stopwords)
num_list = '0123456789'

tweets_df['Tweet'] = tweets_df['Tweet'].apply(
        lambda x: tcf.rmPunctAndStopwords(x, allStopWords, num_list))

# Find the most common words across all tweets
tweet_list = list([x.split() for x in tweets_df['Tweet'] if x is not None])
all_words_counter = Counter(x for xs in tweet_list for x in set(xs))
all_words_counter.most_common(20)

mostCommontweets = pd.DataFrame(all_words_counter.most_common(30),
                                columns=['words', 'count'])
mostCommontweets.head()

# Some visualizations

# 1. Visualize the most common words across all tweets
tcf.plotMostCommonWords(mostCommontweets)


# 2. WordCloud vizualisation

plt.figure(figsize=(10, 10))
gen_text = ' '.join([x for x in tweets_df['Tweet'] if x is not None])
wordcloud = WordCloud().generate(gen_text)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

# 3. Find bigrams (pairs of words that frequently appear next to each other)

# First convert the list of tweets into one consecutive string
allTweetsString = ' '.join([x for x in tweets_df['Tweet']])

bigram_measures = BigramAssocMeasures()

finder = BigramCollocationFinder.from_words(word_tokenize(allTweetsString))

bigramDict = {}
for k, v in finder.ngram_fd.items():
    # We have a condition as we need to avoid characters like '@' and '#'
    if len(k[0]) > 1 and len(k[1]) > 1 and "'s" not in k:
        bigramDict[k] = v
    else:
        continue

# Choose number of bigrams than we want to investigate
topn = 30  # len(bigramDict) -- > if we want all

# Bigrams as a sorted dictionary
sortedBiGrams = sorted(bigramDict.items(),
                       key=lambda x: x[1], reverse=True)[0:topn]

# Visualise the top 20 BiGrams
bgram, counts = list(zip(*sortedBiGrams))
bgstring = list(map(lambda txt: '-'.join(txt), bgram))

plt.figure(figsize=(10, 10))
g = sns.barplot(bgstring, counts, palette='muted')
g.set_xticklabels(g.get_xticklabels(), rotation=80)
plt.title(f'Plot of the top-{topn} pairs of words that appear next to each other')
plt.ylabel('Count')
plt.show()

# 4. Sentiment analysis on tweets based on Liu Hu opinion lexicon
# Classify tweets as 'positive', 'negative' or 'neutral' based on the polarity
# of the words present in a sentence.
sentimentDF = tweets_df.copy()

sentimentDF['Sentiment'] = sentimentDF['Tweet'].apply(lambda tweet:
                                                      tcf.liu_hu_opinion_lexicon(tweet))

# Vizualise the results
plt.figure(figsize=(10, 10))
g = sns.countplot(x=sentimentDF['Sentiment'], data=sentimentDF, palette='deep')
g.set_xticklabels(g.get_xticklabels(), rotation=0)
plt.title(f'Classification of tweets based on Liu-Hu opinion lexicon')
plt.ylabel('Count', labelpad=8)
plt.xlabel('Sentiment', labelpad=8)
plt.show()
