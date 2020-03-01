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
import json
import pandas as pd

from collections import Counter

# Plots and graphs
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

# NLTK module for text preprocessing and analysis
from nltk import word_tokenize
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures

from nltk.corpus import stopwords

# Set up the project environment

# Secure location of the required keys to connect to the API
# This config also contains the search query (in this case 'coronavirus')
json_loc = '/Users/georgiosspyrou/Desktop/config_tweets/Twitter/twitter_config.json'

with open(json_loc) as json_file:
    data = json.load(json_file)

# Project folder location and keys
os.chdir(data["project_directory"])

import twitterCustomFunc as twf

# Import the data from the created .jsonl files

# Read the data from the jsonl files
jsonl_files_folder = os.path.join(data["project_directory"], data["outputFiles"])

# List that will contain all the Tweets that we managed to receive
# via the use of the API

allTweetsList = []

for file in os.listdir(jsonl_files_folder):
    if 'twitter' in file:
        tweets_full_list = twf.loadJsonlData(os.path.join(jsonl_files_folder,
                                                          file))
        allTweetsList += tweets_full_list


# Main exploratory data analysis on the data received from the API.

# Create a dataframe based on the relevant data from the full list of received
# tweets

user_ls, userid_ls, tweet_ls = [], [], []
location_ls, datetime_ls, replyto_ls = [], [], []

for tweet_dict in allTweetsList:
    user_ls.append(tweet_dict['user']['screen_name'])
    userid_ls.append(tweet_dict['user']['id'])
    tweet_ls.append(twf.removeURL(tweet_dict['text']))
    replyto_ls.append(tweet_dict['in_reply_to_user_id'])
    location_ls.append(tweet_dict['user']['location'])
    datetime_ls.append(tweet_dict['created_at'])

# Dataframe that contains the data for analysis
# Note: The twitter API functionality is very broad in what data we can analyse
# This project will focus on tweets and with their respective location/date.
df = pd.DataFrame(list(zip(user_ls, userid_ls, tweet_ls,
                           replyto_ls, location_ls, datetime_ls)),
                  columns=['Username', 'UserID', 'Tweet',
                           'Reply_to', 'Location', 'Date'])

# Remove tweets that they did not have any text
df = df[df['Tweet'].notnull()]

# Remove punctuation and stop words
allStopWords = list(stopwords.words('english'))
spanish_stopwords = list(stopwords.words('spanish'))

# Remove common words used in tweets plus the term that we used for the query
commonTweeterStopwords = ['rt', 'retweet', 'new', 'via', 'us', 'u', '2019',
                          'coronavírus',
                          '#{0}'.format(data['search_query']),
                          '{0}'.format(data['search_query'])]

allStopWords.extend(commonTweeterStopwords + spanish_stopwords)
num_list = '0123456789'

df['Tweet'] = df['Tweet'].apply(lambda x: twf.rmPunctAndStopwords(x, allStopWords, num_list))

# Find the most common words across all tweets

tweet_list = list([x.split() for x in df['Tweet'] if x is not None])
all_words_counter = Counter(x for xs in tweet_list for x in set(xs))
all_words_counter.most_common(20)

mostCommontweets = pd.DataFrame(all_words_counter.most_common(30),
                                columns=['words', 'count'])
mostCommontweets.head()

# Some visualizations

# 1. Visualize the most common words across all tweets
twf.plotMostCommonWords(mostCommontweets)


# 2. WordCloud vizualisation

plt.figure(figsize=(10, 10))
gen_text = ' '.join([x for x in df['Tweet'] if x is not None])
wordcloud = WordCloud().generate(gen_text)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

# 3. Find bigrams (pairs of words that frequently appear next to each other)

# First convert the list of tweets into one consecutive string
allTweetsString = ' '.join([x for x in df['Tweet']])

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

# BiGrams as a dataframe
bigramDF = pd.DataFrame(bigramDict.items(), columns=['BiGram', 'Count'])

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
sentimentDF = df.copy()

sentimentDF['Sentiment'] = sentimentDF['Tweet'].apply(lambda tweet:
                                                      twf.liu_hu_opinion_lexicon(tweet))

# Vizualise the results
plt.figure(figsize=(10, 10))
g = sns.countplot(x=sentimentDF['Sentiment'], data=sentimentDF, palette='deep')
g.set_xticklabels(g.get_xticklabels(), rotation=0)
plt.title(f'Classification of tweets based on Liu-Hu opinion lexicon')
plt.ylabel('Count', labelpad=8)
plt.xlabel('Sentiment', labelpad=8)
plt.show()
