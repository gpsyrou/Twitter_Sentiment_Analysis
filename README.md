## Twitter Topic Modelling and Sentiment Analysis

### Topic: Analysis of Coronavirus related Tweets using TwitterAPI

### Log:
    1) 15/02/2020: The TwitterAPI has a limit of 5000 tweets for the FullArchive version, and 25000 for the 30day version.
		   Need to find a way to receive data for each day for a month period, as the API does not seem to provide this functionality.
    2) 01/03/2020: Version one completed. It included analysis for tweets from 17/01/2020 to 29/02/2020.Tw
		   The analysis is focused on the words that appear frequently in the tweets, as well as analysis on bigrams (words that appear next to each other).
		   Finally we include some analysis on the sentiment of the tweets by using the Hiu Lu opinion lexicon algorithm.
    3) 07/03/2020: Handle non-english tweets (translation) by using a Google translation API 2) Use the location column to identify the longitude and latitude
    4) 14/10/2020: Add data for more months except the initial tweets from January - March. Create a Class for the sentiment analysis. Update the main Jupyter notebook.
	5) 12/11/2020: Version two completed. The jupyter notebook contains data and findings for all months, while analyzing further the months of April, August and October 2020 and compare the change in sentiment. In this version we also include a functionality to plot a geolocation map of the tweets.

### Running Guide for Data Retrieval and Preprocessing
1. Run **data_retrieval.py** to get tweets for a specific period. The script is taking as parameters the start and end date we want to receive data from . It is not recommended to retrieve data for more than a 2-day period in a single API call, as the Twitter API has limits.<br/>
	`python data_retrieval.py 2020-05-15 2020-05-17`
2. Combine the retrieved jsonl files by using the merge_json_files.py script. This will output a text file the contains the combined data<br/>
	`python merge_json_files.py`
3. The data contained in the output text file from step 2 require some preprocessing before we analyze them. In this step we are using the data_preprocessing.py scripts which picks the required data of interest from the text file, removes blank tweets, clean the tweets from hyperlinks, applies translation to the text, and more.<br/>
	`python data_preprocessing.py`

### Useful material while developing:
1) https://twitterdev.github.io/do_more_with_twitter_data/finding_the_right_data.html
2) https://pypi.org/project/searchtweets/
3) https://lucahammer.com/2019/11/05/collecting-old-tweets-with-the-twitter-premium-api-and-python/
4) https://towardsdatascience.com/a-complete-exploratory-data-analysis-and-visualization-for-text-data-29fb1b96fb6a
5) https://www.kaggle.com/caractacus/thematic-text-analysis-using-spacy-networkx
6) https://towardsdatascience.com/the-next-level-of-data-visualization-in-python-dd6e99039d5e
7) https://developer.twitter.com/en/docs/tweets/search/overview/premium
8) https://geopy.readthedocs.io/en/latest/#geopy.extra.rate_limiter.RateLimiter
9) https://plot.ly/python/map-configuration/
10) https://medium.com/@yanlinc/how-to-build-a-lda-topic-model-using-from-text-601cdcbfd3a6
11) https://realpython.com/python-continuous-integration/
