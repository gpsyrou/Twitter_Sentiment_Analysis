
def createTweetWorldMap(df):
    import plotly.graph_objects as go
    
    fig = go.Figure(data=go.Scattergeo(lon = df['Longitude'],
                                       lat = df['Latitude'],
                                       text = df['Tweet'],
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
    
    fig.update_layout(title = 'COVID-19 related Tweets across the world (January 2020 - March 2020) ',
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




