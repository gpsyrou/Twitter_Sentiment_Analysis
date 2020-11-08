"""
-------------------------------------------------------------------
-- Project: Analysis of Coronavirus related Tweets using TwitterAPI
-- Author:  Georgios Spyrou
-- Last Updated:  03/11/2020
-------------------------------------------------------------------
"""
import os
import json
import argparse

import pandas as pd
import numpy as np
from datetime import datetime
import time

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut
from sentiment_class import month_as_string

import utilities.plot_world_map as pmap
from sentiment_class import TwitterSentiment, month_as_string

json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    config = json.load(json_file)

# Project folder location and keys
os.chdir(config["project_directory"])

geolocator = Nominatim(user_agent="https://developer.twitter.com/en/apps/17403833") 
   
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=2)

translated_tweets_filename = 'tweets_translated.csv'

parser=argparse.ArgumentParser()
parser.add_argument('input_year', type=int)
parser.add_argument('input_month', type=int)
args = parser.parse_args()

def get_valid_coordinates(location: str, geolocator: Nominatim) -> list:
    """
    Given a string which is pointing to specific location (e.g. 'London'),
    return the Latitude and Longitude coordinates of each entry. 
    If an entry does not correspond to a place (e.g. 'abcdef') then return None.
    """
    if (location is not None) and (str(location) != 'nan'):
        try:
            print(f'Location:.... {location}')
            try:
                coordinates = geolocator.geocode(location)
                lat = coordinates.point[0]
                long = coordinates.point[1]
                return lat, long
            except AttributeError:
                return 'No latitude', 'No longitude'
        except GeocoderTimedOut:
            return get_valid_coordinates(location, geolocator)
    else:
            return 'No latitude', 'No longitude'


tweets_df = pd.read_csv(translated_tweets_filename, sep='\t', encoding = 'utf-8', index_col=[0])

tweets_df = tweets_df[tweets_df['Tweets_Clean'].notnull()].reset_index()

df_subset = TwitterSentiment(input_df=tweets_df, tweet_column='Tweets_Clean')
df_subset.subset_dataframe(year=args.input_year, month=args.input_month)

df_with_coordinates = df_subset.df
df_with_coordinates.reset_index(drop=True, inplace=True)


for i in range(0, df_with_coordinates.shape[0]):
    if (i != 0) and (i%100 == 0):
        time.sleep(120)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)
    
    print('Index.. {0}'.format(i))
    location = df_with_coordinates['Location'].iloc[i]

    latitude, longitude = get_valid_coordinates(location, geolocator)

    df_with_coordinates.loc[i, 'Latitude'] = latitude
    df_with_coordinates.loc[i, 'Longitude'] = longitude
    print('Location found in: [{0}, {1}]'.format(latitude, longitude))

month = month_as_string(args.input_month)

geoloc_filaname = os.path.join(config['geolocation_data_folder'], f'tweets_with_geolocation_{month}_{args.input_year}.csv')
df_with_coordinates.to_csv(geoloc_filaname, sep='\t', encoding='utf-8', index=False)
