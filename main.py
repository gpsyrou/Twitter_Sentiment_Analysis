"""
-------------------------------------------------------------------
-- Project:  Analysis of Coronavirus related Tweets using TwitterAPI
-- Author:  Georgios Spyrou
-- Last Updated:  10/09/2020
-------------------------------------------------------------------
"""
import pandas as pd
import json
import os
import seaborn as sns

json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    config = json.load(json_file)
    
# Project folder location and keys
os.chdir(config["project_directory"])

import utilities.twitter_custom_functions as tcf
from sentiment_class import TwitterSentiment

sns.set_style("darkgrid")

translated_tweets_filename = 'tweets_translated.csv'

# Import the latest version of the csv that holds the translated data
tweets_df = pd.read_csv(translated_tweets_filename, sep='\t',
                        encoding = 'utf-8', index_col=[0])

tweets_df = tweets_df[tweets_df['Tweets_Clean'].notnull()].reset_index()

# 1. Visualize the most common words across all tweets

# All
tweets_all_months = TwitterSentiment(input_df=tweets_df,
                                              tweet_column='Tweets_Clean')
tweets_all_months.plot_most_common_words(n_most_common=10, figsize=(10, 8))

# August
tweets_august = TwitterSentiment(input_df=tweets_df,
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

# August
tweets_august.calculate_sentiment()
tweets_august.plot_sentiment(figsize=(10, 8))





# Unfortunately TwitterAPI doesn't give much information regarding coordinates.
# But we can try to find the geolocation (long/lat) through the use of geopy
# Geopy has a limit in the times we can call it per second so we have to find
# a workaround
august_df = tweets_august.df

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import utilities.plot_world_map as pmap

geolocator = Nominatim(user_agent="https://developer.twitter.com/en/apps/17403833") 
   
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1,
                      max_retries=3, error_wait_seconds=2)

# Split it in batches and identify the locations
august_df_min = august_df.iloc[0:120]

august_df_min['Point'] = august_df_min['Location'].apply(lambda x: tcf.get_valid_coordinates(x, geolocator))

dfWithCoords = august_df_min[august_df['Point'].notnull()]
dfWithCoords['Latitude'] = dfWithCoords['Point'].apply(lambda x: x[0])
dfWithCoords['Longitude'] = dfWithCoords['Point'].apply(lambda x: x[1])

fig = pmap.create_tweet_worldmap(dfWithCoords)
plt.plot(fig)