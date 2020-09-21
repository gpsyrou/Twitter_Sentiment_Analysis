import pandas as pd
import pickle
import json
import os
import sys
sys.path.append('../') 
import seaborn as sns

from nltk.corpus import stopwords

from Code.sentiment_class import TwitterSentiment


json_loc = r'D:\GitHub\Projects\Twitter_Project\Twitter_Topic_Modelling\twitter_config.json'

with open(json_loc) as json_file:
    config = json.load(json_file)

# Project folder location and keys
os.chdir(config["project_directory"])