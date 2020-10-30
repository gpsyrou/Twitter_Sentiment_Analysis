"""
-------------------------------------------------------------------
-- Title:   Analysis of Coronavirus related Tweets using TwitterAPI
-- File:    plotWorldMap.py
-- Purpose: Functions regarding the plotting of tweets as a world map with
            plotly.
-- Author:  Georgios Spyrou
-- Last Updated:  08/03/2020 15:35:28
-------------------------------------------------------------------
"""

import pandas as pd
from plotly import graph_objs as go


def create_tweet_worldmap(df: pd.core.frame.DataFrame, tweets_column='Tweet'):
    """
    Given dataframe that contains columns corresponding to Longitude and Latitude,
    create a world map plot and mark the Tweet locations on the map.
    
    """
    df['Text'] = df['Date'] + ': \n' + df[tweets_column]
    
    fig = go.Figure(data=go.Scattergeo(lon = df['Longitude'],
                                       lat = df['Latitude'],
                                       text = df['Text'],
                                       mode = 'markers',
                                       marker = dict(
                                     			symbol = 'circle',
                                     			line = dict(
                                     						width=1,
                                     						color='rgba(102, 102, 102)'
                                     						),
                                     			colorscale = 'Viridis',
                                     			cmin = 0,
            )))
    
    fig.update_layout(title = 'COVID-19 related Tweets across the world (January 2020 - October 2020) ',
                      geo_scope='world',
                      			geo = dict(
            			resolution = 110,
            			scope = 'world',
    					showland = True,
    					landcolor = "rgb(250, 250, 250)",
    					subunitcolor = "rgb(217, 217, 217)",
    					countrycolor = "rgb(217, 217, 217)",
    					countrywidth = 0.6,
    					subunitwidth = 0.6,
    					))
    return fig




