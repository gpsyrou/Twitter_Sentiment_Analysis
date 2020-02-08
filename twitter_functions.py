import re
import string
import matplotlib.pyplot as plt
from nltk.tokenize import TweetTokenizer

def removeURL(text):
    '''
    Removes URLs (strings that start with 'http\\ or htpps\\) from text
    
    Parameters
    ---
        text: str
    
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
    

def rmPunctAndStopwords(text, stopwordlist, num_list):
    '''
    Given text, remove stopwords and punctuation from the string and convert
    all characters to lowercase.
    
    Parameters
    ---
    text : str
            Input text for cleaning.
    stopwordlist: list
            List of stopwords to be removed from the string.
    num_list: list
            List of numbe of number to be removed from the string.
    '''

    tknzr = TweetTokenizer()
    try:
        txt_tokenized = tknzr.tokenize(text)
        text = ' '.join([char.lower() for char in txt_tokenized if char 
                         not in string.punctuation and char not in stopwordlist
                         and char != '…' and char not in num_list])
    except TypeError:
       pass
   
    return text


def plotMostCommonWords(counterDataFrame):
    '''
    Plot the most common words that appear in a corpus.
    
    Parameters
    ---
    counterList: Dataframe
            Contains a dataframe of the form ['word','count'] 
            
    Result
    ---
    Returns a plot of the most common words.
        
    '''
    fig, ax = plt.subplots(figsize=(10, 10))

    counterDataFrame.sort_values(by='count').plot.barh(x='words',
                          y='count',
                          ax=ax,
                          color="purple")
    plt.grid(True, alpha = 0.3)
    ax.set_title("Common Words Found in Tweets (Without Stop Words)")
    
    plt.show()
