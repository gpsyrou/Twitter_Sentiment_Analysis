## Twitter_Topic_Modelling

### Topic: Analysis of Coronavirus related Tweets using TwitterAPI

### Log:
    1) 15/02/2020: The TwitterAPI has a limit of 5000 tweets for the FullArchive version, and 25000 for the 30day version.
		   Need to find a way to receive data for each day for a month period, as the API does not seem to provide this functionality.
    2) 01/03/2020: Version one completed. It included analysis for tweets from 17/01/2020 to 29/02/2020. The analysis is focused on the words that appear frequently in the tweets, as well as analysis on bigrams (words that appear next to each other). Finally we include some analysis on the sentiment of the tweets by using the Hiu Lu opinion lexicon algorithm.
	
### Useful material while developing:
1) https://twitterdev.github.io/do_more_with_twitter_data/finding_the_right_data.html
2) https://pypi.org/project/searchtweets/
3) https://lucahammer.com/2019/11/05/collecting-old-tweets-with-the-twitter-premium-api-and-python/
4) https://towardsdatascience.com/a-complete-exploratory-data-analysis-and-visualization-for-text-data-29fb1b96fb6a
5) https://www.kaggle.com/caractacus/thematic-text-analysis-using-spacy-networkx
