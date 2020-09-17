"""
-------------------------------------------------------------------
-- Title:   Analysis of Coronavirus related Tweets using TwitterAPI
-- File:    twitterCustomFunc.py
-- Purpose: Custom functions used for the project.
-- Author:  Georgios Spyrou
-- Last Updated:  15/02/2020 10:33:47
-------------------------------------------------------------------
"""

# Dependencies used from the functions
import re
import string
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

import json
import json_lines

import matplotlib.pyplot as plt
from wordcloud import WordCloud

from nltk.tokenize import TweetTokenizer
from googletrans import Translator

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
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
        txt_tokenized = tknzr.tokenize(text)
        text = ' '.join([char.lower() for char in txt_tokenized if char.lower() 
                         not in string.punctuation and char.lower() not in
                         stopwordlist and char not in num_list])
    except TypeError:
       pass
   
    return text


def plot_most_common_words(counterDataFrame: pd.core.frame.DataFrame, year: int,
                        month: int) -> list:

    year_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May',
                 6:'June', 7:'July', 8:'August', 9:'September', 10:'October',
                 11:'Novermber', 12:'December'}

    fig, ax = plt.subplots(figsize=(10, 10))

    counterDataFrame.sort_values(by='count').plot.barh(x='words', y='count',
                          ax=ax, color="purple")
    plt.grid(True, alpha = 0.3, linestyle='-', color='black')
    ax.set_title(f'Common Words Found in Tweets - {year_dict[month]} {year}',
                 fontweight='bold')
    
    plt.show()


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


def liu_hu_opinion_lexicon(sentence: str) -> str:
    """
    Modified version of the Liu Hu opinion lexicon algorithm for sentiment
    analysis on sentences.
    Reference: https://www.nltk.org/_modules/nltk/sentiment/util.html#demo_liu_hu_lexicon
    
    The function has been modified to return the values instead of printing.
    
    Returns:
    --------
    Sentiment of a sentence, classified as 'Positive', 'Negative' or 'Neutral'
    """
    
    from nltk.corpus import opinion_lexicon
    from nltk.tokenize import treebank

    tokenizer = treebank.TreebankWordTokenizer()
    pos_words, neg_words = 0,0
    y = []
    tokenized_sent = [word.lower() for word in tokenizer.tokenize(sentence)]

    for word in tokenized_sent:
        if word in opinion_lexicon.positive():
            pos_words += 1
            y.append(1)  # positive
        elif word in opinion_lexicon.negative():
            neg_words += 1
            y.append(-1)  # negative
        else:
            y.append(0)  # neutral

    if pos_words > neg_words:
        return('Positive')
    elif pos_words < neg_words:
        return('Negative')
    elif pos_words == neg_words:
        return('Neutral')
    
    
def translate_tweet(text: str) -> str:
    """
    If Tweets are written in any other language than English, translate to
    English and return the translated string.
    """
    translator = Translator(service_urls=['translate.google.com'])
    try:
        textTranslated = translator.translate(text, dest='en').text
    except json.JSONDecodeError:
        textTranslated = text
        pass
    return textTranslated


def get_valid_coordinates(location: str, geolocator: Nominatim) -> list:
    """
    Given a string which is pointing to specific location (e.g. 'London'),
    return the Latitude and Longitude coordinates of each entry. 
    If an entry does not correspond to a place (e.g. 'abcdef') then we return None.
    """
    
    try:
        if location is not None:
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


def most_common_words(input_df: pd.core.frame.DataFrame, col: str,
                      n_most_common=20) -> pd.core.frame.DataFrame:
    """
    Calculate the most common words of a categorical column, usually in a
    format of text.

    Args:
    ------
        input_df: Dataframe that contains the relevant text column
        col: Name of the column
        year: If not None, then indicate year of tweet was made
        month: If not None, then indicate month of tweet was made
        n_most_common: Number of most common words to calculate
    Returns:
    --------
        Pandas dataframe with two columns indicating a word and number of times
        (count) that it appears in the original input_df
    """
    word_list = list([x.split() for x in input_df[col] if x is not None])
    word_counter = Counter(x for xs in word_list for x in set(xs))
    word_counter.most_common(n_most_common)
    
    common_words_df = pd.DataFrame(word_counter.most_common(n_most_common),
                                columns=['words', 'count'])
    return common_words_df


def plot_wordcloud(input_df: pd.core.frame.DataFrame, col: str,
                   figsize=(10, 8))-> None:
    """
    Generate a WordCloud plot based on the number of occurenences of words
    in a set of text or documents
    """
    plt.figure(figsize=figsize)
    gen_text = ' '.join([x for x in input_df[col] if x is not None])
    wordcloud = WordCloud().generate(gen_text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def filter_df(input_df: pd.core.frame.DataFrame, year: int, month: int):
    """
    Filter the master dataframe on a subset depending on a combination of year
    and month of interest.
    """
    if year not in list(input_df['Year'].unique()):
        print('This year does not exist')
    elif month not in list(input_df['Month'].unique()):
        print('This month does not exist')
    else:
        filtered_df = input_df[(input_df['Year']==year) & (input_df['Month']==month)]
        return filtered_df

