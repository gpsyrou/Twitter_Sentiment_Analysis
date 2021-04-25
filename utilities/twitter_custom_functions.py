"""
-------------------------------------------------------------------
-- Project:  Analysis of Coronavirus related Tweets using TwitterAPI
-- Author:  Georgios Spyrou
-- Last Updated: 19/09/2020
-------------------------------------------------------------------
"""

import re
import string
from datetime import datetime, timedelta

import json
import json_lines

from nltk.tokenize import TweetTokenizer
from googletrans import Translator

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def load_jsonl_data(file: str) -> list:
    """
    Reads the data as saved in a .jsonl file
    
    Args:
    ----
    file: String corresponding to the path to a .jsonl file which contains the 
          tweets as received from the TwitterAPI.

    Returns:
    -------
    tweets: A list of all the data saved in the .jsonl file.
    """
    
    tweets = []
    with open(file, 'rb') as f:
        for tweet in json_lines.reader(f, broken=True):
            try:
                tweets.append(tweet)
            except json_lines.UnicodeDecodeError or json.JSONDecodeError:
                pass

        return tweets


def remove_url(text: str) -> str:
    """
    Removes URLs (strings that start with 'http\\ or htpps\\) from text
    
    Args:
    ----
        text: Input string the we want to remove the URL from.
     
    Returns:
    -------
    text: The input string clean from any URL.
    """

    regex = r'http[0-9a-zA-Z\\/.:]+.'
    urllinks = re.findall(regex, text)
    if  urllinks != []:
        for url in urllinks:
            print(f'String removed: {url}')
            if type(url) is tuple:
                url = [x for x in url if x != '']
            try:
                text = text.replace(url,'')
            except TypeError:
                continue
        return text
    else:
        pass
    

def remove_punct_and_stopwords(text: str, stopwordlist: list,
                               num_list: list) -> str:
    """
    Given text, remove stopwords and punctuation from the string and convert
    all characters to lowercase.
    
    Args:
    ----
    text : str
            Input text for cleaning.
    stopwordlist: list
            List of stopwords to be removed from the string.
    num_list: list
            List of number to be removed from the string.
    
    Returns:
    -------
    text: str
        The input string as lowercase, clean from stopwords/punctuation/numbers
    """

    tknzr = TweetTokenizer()
    try:
        text_lower = text.lower()
        txt_tokenized = tknzr.tokenize(text_lower)
        text = ' '.join([char for char in txt_tokenized if char not in string.punctuation and char not in stopwordlist and char not in num_list])
    except TypeError:
       pass
   
    return text


def create_date_time_frame(day: str, hourSep: int) -> list:
    """
    Given a specific day of the year, split the day into n amount of timeframes
    
    Args:
    ----
    day: Day of the year in a "%Y-%m-%d" format.
    hourSep: Number of hours to add in each timeframe.
    
    Returns:
    --------
    timeFrameList: List of equally splitted timeframes for the day.
    
    #TODO: make hourDivisionsList a parameter
    
    """
    hourDivisionsList = ['00:45', '03:45', '06:45','09:45', '12:45',
                         '15:45', '18:45', '21:45']
    timeFrameList = []
    for tframe in hourDivisionsList:
        datePart = day + f' {tframe}'
        date = datetime.strptime(datePart, "%Y-%m-%d %H:%M")
        mod_date = date + timedelta(hours=2)
        incrementedDate = datetime.strftime(mod_date, "%Y-%m-%d %H:%M")
    
        timeFrameList.append([datePart, incrementedDate])
    
    return timeFrameList

 
def translate_tweet(input_text: str) -> str:
    """
    Given text which is written in any other language than English, translate to
    English and return the translated string.
    """
    translator = Translator(service_urls=['translate.google.com'])
    print(input_text)
    try:
        language_detected = translator.detect(input_text)
        if language_detected.lang != 'en':
            try:
                input_text = translator.translate(input_text, dest='en').text
            except json.JSONDecodeError:
                pass
    except AttributeError:
        pass
    return input_text


def get_valid_coordinates(location: str, geolocator: Nominatim) -> list:
    """
    Given a string which is pointing to specific location (e.g. 'London'),
    return the Latitude and Longitude coordinates of each entry. 
    If an entry does not correspond to a place (e.g. 'abcdef') then we return None.
    """
    
    try:
        if (location is not None) and (str(location) != 'nan'):
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
