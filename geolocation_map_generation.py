import pandas as pd
from datetime import datetime
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut

import utilities.plot_world_map as pmap
from sentiment_class import TwitterSentiment, month_as_string


geolocator = Nominatim(user_agent="https://developer.twitter.com/en/apps/17403833") 
   
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=2)

def get_valid_coordinates(location: str, geolocator: Nominatim) -> list:
    """
    Given a string which is pointing to specific location (e.g. 'London'),
    return the Latitude and Longitude coordinates of each entry. 
    If an entry does not correspond to a place (e.g. 'abcdef') then return None.
    """
    try:
        print(f'Location:.... {location}')
        try:
            coordinates = geolocator.geocode(location)
            lat = coordinates.point[0]
            long = coordinates.point[1]
            return [lat, long]
        except AttributeError:
            return None
        else:
            pass
    except GeocoderTimedOut:
        return get_valid_coordinates(location, geolocator)


translated_tweets_filename = 'tweets_translated.csv'
tweets_df = pd.read_csv(translated_tweets_filename, sep='\t', encoding = 'utf-8', index_col=[0])

tweets_df = tweets_df[tweets_df['Tweets_Clean'].notnull()].reset_index()

tweets_february = TwitterSentiment(input_df=tweets_df, tweet_column='Tweets_Clean')
tweets_february.subset_dataframe(year=2020, month=2)
tweets_february.df.shape


for i in range(0, tweets_february.df.shape[0]):
    if (i != 0) and (i%100 == 0):
        time.sleep(180)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)
    
    print('Index.. {0}'.format(i))
    coords = get_valid_coordinates(tweets_february.df['Location'].iloc[i], geolocator)
    tweets_february.df.loc[i, 'Latitude'] = coords[0]
    tweets_february.df.loc[i, 'Longitude'] = coords[1]
    print('\nLocation found in: {0}'.format(coords))
