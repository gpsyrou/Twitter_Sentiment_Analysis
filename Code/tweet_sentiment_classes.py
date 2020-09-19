import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

from collections import Counter

class TweetSentimentDataframe:
 
    
    def __init__(self, input_df, tweet_column):
        self.df = input_df
        self.year = None
        self.month = None
        self.tweet_column = tweet_column
            
    def subset_dataframe(self, year:int, month: int):
        """
        Filter the master dataframe on a subset depending on a combination of year
        and month of interest.
        """
        self.year = year
        self.month = month

        if year not in list(self.df['Year'].unique()):
            print('This year does not exist')
        elif month not in list(self.df['Month'].unique()):
            print('This month does not exist')
        else:
            self.df = self.df[(self.df['Year']==year) & (self.df['Month']==month)]


    def most_common_words(self, tweet_column: str, n_most_common=20) -> pd.core.frame.DataFrame:
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
        

        word_list = list([x.split() for x in self.df[self.tweet_column] if x is not None])
        word_counter = Counter(x for xs in word_list for x in set(xs))
        word_counter.most_common(n_most_common)
        
        self.common_words_df = pd.DataFrame(word_counter.most_common(n_most_common),
                                    columns=['words', 'count'])
        return self.common_words_df


    def plot_most_common_words(self, figsize=(10, 10)):
    
        year_dict = {1:'January', 2:'February', 3:'March', 4:'April',
                     5:'May', 6:'June', 7:'July', 8:'August',
                     9:'September', 10:'October', 11:'Novermber',
                     12:'December'}
    
        fig, ax = plt.subplots(figsize=figsize)
        common_words_df = self.most_common_words(tweet_column=self.tweet_column)
        common_words_df.sort_values(by='count').plot.barh(x='words',
                                   y='count', ax=ax, color='purple')
        plt.grid(True, alpha = 0.3, linestyle='-', color='black')
        if self.year is not None and self.month is not None:
            ax.set_title(f'Common Words Found in Tweets - {year_dict[self.month]} {self.year}',
                                                           fontweight='bold')
        else:
            ax.set_title(f'Common Words Found in Tweets', fontweight='bold')                
        plt.show()