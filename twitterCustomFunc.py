"""
-------------------------------------------------------------------
-- Title:   Analysis of Coronavirus related Tweets using TwitterAPI
-- File:    twitterCustomFunc.py
-- Purpose: Custom functions used for the project.
-- Author:  Georgios Spyrou
-- Date:    15/02/2020 10:33:47
-------------------------------------------------------------------
"""

# Dependencies used from the functions
import re
import string
import pandas as pd
import json
import json_lines
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from nltk.tokenize import TweetTokenizer


def loadJsonlData(file: str) -> list:
    '''
    Reads the data as saved in a .jsonl file
    
    Args:
    ----
    file: String corresponding to the path to a .jsonl file which contains the 
          tweets as received from the TwitterAPI.

    Returns:
    -------
    tweets: A list of all the data saved in the .jsonl file.
    '''
    
    tweets = []
    with open(file, 'rb') as f:
        for tweet in json_lines.reader(f, broken=True):
            try:
                tweets.append(tweet)
            except json_lines.UnicodeDecodeError or json.JSONDecodeError:
                pass

        return tweets


def removeURL(text: str) -> str:
    '''
    Removes URLs (strings that start with 'http\\ or htpps\\) from text
    
    Args:
    ----
        text: Input string the we want to remove the URL from.
     
    Returns:
    -------
    text: The input string clean from any URL.
    '''

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
    

def rmPunctAndStopwords(text: str, stopwordlist: list, num_list: list) -> str:
    '''
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
    '''

    tknzr = TweetTokenizer()
    try:
        txt_tokenized = tknzr.tokenize(text)
        text = ' '.join([char.lower() for char in txt_tokenized if char.lower() 
                         not in string.punctuation and char.lower() not in stopwordlist
                         and char != '…' and char != '...' and char != '’' and char not in num_list])
    except TypeError:
       pass
   
    return text


def plotMostCommonWords(counterDataFrame: pd.core.frame.DataFrame) ->list:
    '''
    Plot the most common words that appear in a corpus.
    
    Args:
    ----
    counterDataFrame: Dataframe
            Contains a dataframe of the form ['word','count'] 
            
    Returns:
    -------
    A plot of the most common words.
        
    '''
    fig, ax = plt.subplots(figsize=(10, 10))

    counterDataFrame.sort_values(by='count').plot.barh(x='words',
                          y='count',
                          ax=ax,
                          color="purple")
    plt.grid(True, alpha = 0.3)
    ax.set_title("Common Words Found in Tweets (Without Stop Words)")
    
    plt.show()

def createDateTimeFrame(day: str, hourSep: int) -> list:
    '''
    Given a specific day of the year, split the day into n amount of timeframes
    
    Args:
    ----
    day: Day of the year in a "%Y-%m-%d" format.
    hourSep: Number of hours to add in each timeframe.
    
    Returns:
    --------
    timeFrameList: List of equally splitted timeframes for the day.
    
    #TODO: make hourDivisionsList a parameter
    
    '''
    hourDivisionsList = ['09:00', '15:00', '19:00', '21:00']
    timeFrameList = []
    for tframe in hourDivisionsList:
        datePart = day + f' {tframe}'
        date = datetime.strptime(datePart, "%Y-%m-%d %H:%M")
        mod_date = date + timedelta(hours=2)
        incrementedDate = datetime.strftime(mod_date, "%Y-%m-%d %H:%M")
    
        timeFrameList.append([datePart, incrementedDate])
    
    return timeFrameList

def liu_hu_opinion_lexicon(sentence: str) -> str:
    '''
    Modified version of the Liu Hu opinion lexicon algorithm for sentiment
    analysis on sentences.
    Reference: https://www.nltk.org/_modules/nltk/sentiment/util.html#demo_liu_hu_lexicon
    
    The function has been modified to return the values instead of printing.
    
    Returns:
    --------
    Sentiment of a sentence, classified as 'Positive', 'Negative' or 'Neutral'
    '''
    
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
