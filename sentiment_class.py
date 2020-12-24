"""
-------------------------------------------------------------------
-- Project: Analysis of Coronavirus related Tweets using TwitterAPI
-- Author: Georgios Spyrou
-- Last Updated: 19/09/2020
-------------------------------------------------------------------
"""

import matplotlib.pyplot as plt

from collections import Counter
from pandas import DataFrame

from wordcloud import WordCloud
from seaborn import barplot, countplot

from nltk.collocations import BigramCollocationFinder
from nltk import word_tokenize


def month_as_string(month_as_int: int) -> str:
    """
    Take an integer as input representing a month, and return the corresponding
    month as a string (e.g. 1 -> January)
    """
    year_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'Novermber',
            12: 'December'}
    
    return year_dict[month_as_int]


class TwitterSentiment:

    def __init__(self, input_df, tweet_column):
        self.df = input_df
        self.year = None
        self.month = None
        self.tweet_column = tweet_column

    def subset_dataframe(self, year: int, month: int):
        """
        Filter the master dataframe on a subset depending on a combination of
        year and month of interest.
        """
        self.year = year
        self.month = month

        if year not in list(self.df['Year'].unique()):
            print('This year does not exist')
        elif month not in list(self.df['Month'].unique()):
            print('This month does not exist')
        else:
            self.df = self.df[(self.df['Year'] == year) &
                              (self.df['Month'] == month)]

    def most_common_words(self, tweet_column: str, n_most_common=20):
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
            Pandas dataframe with two columns indicating a word and number
            of times (count) that it appears in the original input_df
        """
        word_list = list([x.split() for x in self.df[self.tweet_column] if x is not None])
        word_counter = Counter(x for xs in word_list for x in set(xs))
        word_counter.most_common(n_most_common)

        self.common_words_df = DataFrame(word_counter.most_common(
                n_most_common), columns=['words', 'count'])
        return self.common_words_df

    def plot_most_common_words(self, n_most_common=20, figsize=(10, 10)) -> None:

        fig, ax = plt.subplots(figsize=figsize)
        common_words_df = self.most_common_words(tweet_column=self.tweet_column,
                                                 n_most_common=n_most_common)
        barplot(x='count', y='words', data=common_words_df)

        plt.grid(True, alpha=0.3, linestyle='-', color='black')

        if self.year is not None and self.month is not None:
            ax.set_title(f'Common Words Found in Tweets - {month_as_string(self.month)} {self.year}',
                                                           fontweight='bold')
        else:
            ax.set_title(f'Common Words Found in Tweets - Overall', fontweight='bold')         
        plt.show()

    def plot_wordcloud(self, figsize=(10, 10)) -> None:
        """
        Generate a WordCloud plot based on the number of occurenences of words
        in a set of text or documents
        """
        plt.figure(figsize=figsize)
        gen_text = ' '.join([x for x in self.df[self.tweet_column] if x is not None])
        wordcloud = WordCloud().generate(gen_text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

    def compute_bigrams(self) -> dict:
        """
        Calculate the number of occurences that a pair of words appear next to
        each other, and return a dictionary of pair of words - count.
        """
        tweets_to_string = ' '.join([x for x in self.df[self.tweet_column]])

        finder = BigramCollocationFinder.from_words(word_tokenize(tweets_to_string))

        bigrams_dict = {}
        for k, v in finder.ngram_fd.items():
            # Condition to avoid characters like '@' and '#'
            if len(k[0]) > 1 and len(k[1]) > 1 and "'s" not in k:
                bigrams_dict[k] = v
            else:
                continue
        return bigrams_dict

    def plot_bigrams(self, top_n: int, figsize=(10, 8)) -> None:

        bigrams_dict = self.compute_bigrams()
        sortedBiGrams = sorted(bigrams_dict.items(), key=lambda x: x[1],
                               reverse=True)[0:top_n]

        bgram, counts = list(zip(*sortedBiGrams))
        bgstring = list(map(lambda txt: '-'.join(txt), bgram))

        plt.figure(figsize=figsize)
        g = barplot(bgstring, counts, palette='muted')
        g.set_xticklabels(g.get_xticklabels(), rotation=80)
        plt.title(f'Top-{top_n} pairs of words that appear next to each other',
                  fontweight='bold')
        plt.ylabel('Count')
        plt.grid(True, alpha=0.2, color='black')
        plt.show()    

    def liu_hu_opinion_lexicon(self, sentence: str) -> str:
        """
        Modified version of the Liu Hu opinion lexicon algorithm for sentiment
        analysis on sentences.
        Reference: https://www.nltk.org/_modules/nltk/sentiment/util.html#demo_liu_hu_lexicon

        The function has been modified to return the values instead of printing

        Returns:
        --------
        Sentiment of a text, classified as 'Positive','Negative' or 'Neutral'
        """

        from nltk.corpus import opinion_lexicon
        from nltk.tokenize import treebank
    
        tokenizer = treebank.TreebankWordTokenizer()
        pos_words, neg_words = 0, 0
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

    def calculate_sentiment(self):
        """
        Calculate the sentiment of a column by using the liu_hu_opinion_lexicon method
        and output the result into a Sentiment column
        """
        self.df['Sentiment'] = self.df[self.tweet_column].apply(lambda tweet:
            self.liu_hu_opinion_lexicon(tweet))
   
    def plot_sentiment(self, sentiment_month=None, year=None, figsize=(10, 8)) -> None:
        plt.figure(figsize=figsize)
        if sentiment_month is not None:
            sentiment_df = self.df[self.df['Month'] == sentiment_month]
            title_str = f'Sentiment Classification of Tweets - {month_as_string(sentiment_month)} {year}'
        else:
            sentiment_df = self.df
            title_str = 'Sentiment Classification of Tweets'
        clr_palette = {'Positive': '#37B41E', 'Neutral': '#1B9EC8', 'Negative':'#C92528'}
        g = countplot(x='Sentiment', data=sentiment_df, palette=clr_palette, order=['Negative', 'Neutral', 'Positive'])
        g.set_xticklabels(g.get_xticklabels(), rotation=0)
        plt.title(title_str, fontweight='bold')
        plt.ylabel('Count', labelpad=8)
        plt.xlabel('Sentiment', labelpad=8)
        plt.show()
