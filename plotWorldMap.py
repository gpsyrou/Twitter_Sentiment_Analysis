from plotly.offline import plot
import pandas as pd


#make a data dictionary
data = [dict(
			type = 'scattergeo',
			lon = dftemp['Longitude'],
			lat = dftemp['Latitude'],
			mode = 'markers',
			marker = dict(
			symbol = 'circle',
			line = dict(
						width=1,
						color='rgba(102, 102, 102)'
						),
			colorscale = 'Viridis',
			cmin = 0,
        ))]

#define the layout
layout = dict(
			title = 'Tweets over the world',
			geo = dict(
        			resolution = 50,
        			scope = 'world',
					showland = True,
					landcolor = "rgb(250, 250, 250)",
					subunitcolor = "rgb(217, 217, 217)",
					countrycolor = "rgb(217, 217, 217)",
					countrywidth = 0.5,
					subunitwidth = 0.5,
					center = dict(
								lon = 39.0,
								lat = 21.8
								),
					projection = dict(
								scale = 0.05
								),
					lonaxis = dict(
								 range= [ -127.0, -114.0 ]
								 ),
					lataxis = dict(
								 range= [ 35.0, 38.0 ] 
								 ),
					),
			)
#add data and layout to figure
fig = dict(
		data=data,
		layout=layout
		)
#plot
plot(fig)