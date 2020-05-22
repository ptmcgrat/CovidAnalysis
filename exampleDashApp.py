import dash, json, pdb
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from dash.dependencies import Input, Output

import pandas as pd
from urllib.request import urlopen

herd_immunity = 0.7
mapbox_token = 'pk.eyJ1IjoicHRtY2dyYXQiLCJhIjoiY2thZjlzcWdhMHUzaDJ4bGR4cm41cngxbSJ9.jdu2nc1epqcHux0x0wGn6g'


demographics = pd.read_csv('CreatedData/Demographics.csv', dtype = {'countyFIPS':'str'})
IFR = pd.read_csv('CreatedData/RelativeCovidRiskNormalDeath.csv')
cases = pd.read_csv('CreatedData/CovidCasesDeaths.csv',dtype = {'countyFIPS':'str'})

predictedDeaths = pd.merge(demographics[demographics.Level=='County'], IFR, on = 'Age')
predictedDeaths['PredictedDied'] = (predictedDeaths['#Alive']*predictedDeaths['IFR_Probable']*herd_immunity).astype('int')
predictedDeaths['AgeGroups'] = (10*(predictedDeaths['Age']/10).astype('int')).astype('str') + 'to' + (10 + 10*(predictedDeaths['Age']/10).astype('int')).astype('str')
predictedDeaths.loc[predictedDeaths['AgeGroups'] == '100to110', 'AgeGroups'] = '90+'
predictedDeaths.loc[predictedDeaths['AgeGroups'] == '90to100', 'AgeGroups'] = '90+'

AgeStratification = predictedDeaths.groupby('AgeGroups')[['#Alive', 'PredictedDied']].sum()
AgeStratification['IFR'] = AgeStratification['PredictedDied']/AgeStratification['#Alive']*100

predictedDeaths = predictedDeaths.groupby(['PopulationID','countyFIPS', 'State']).sum()[['#Alive','PredictedDied']].reset_index()
predictedDeaths['PredictedDied'] = predictedDeaths['PredictedDied'].astype('int')

all_dt = pd.merge(predictedDeaths, cases, on = 'countyFIPS')

all_dt['Total Cases per 100,000'] = all_dt['CurrentCases']/(all_dt['#Alive'])*100000
all_dt['Percent of Predicted Deaths'] = all_dt['CurrentDeaths']/all_dt['PredictedDied']*100
all_dt['Predicted IFR'] = all_dt['PredictedDied']/all_dt['#Alive']*100
all_dt['New Cases per 100,000'] = all_dt['DeltaCases']/(all_dt['#Alive'])*100000
all_dt['New Deaths per 100,000'] = all_dt['DeltaDeaths']/(all_dt['#Alive'])*100000

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
	counties = json.load(response)

map_types = {'Total Cases per 100,000':5000, 'Percent of Predicted Deaths':25, 'New Cases per 100,000':500, 'New Deaths per 100,000':50}
maps = []

for map_type in map_types:
	maps.append(go.Choroplethmapbox(
        name = map_type,
		geojson = counties,
		locations = all_dt.countyFIPS.tolist(),
		z = all_dt[map_type].tolist(),
		text = all_dt.PopulationID.tolist(),
		visible=False,
		subplot='mapbox1',
        colorscale="Viridis",
        zmin = 0,
        zmax = map_types[map_type]
		))
maps[0]['visible'] = True

#fig.show()
#fig = ff.create_choropleth(fips = all_dt['countyFIPS'], values = all_dt['Total Cases per 100,000'])
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#fig.plot()

layout = go.Layout(
	mapbox1 = dict(
	#domain = {'x': [0.3, 1],'y': [0, 1]},
	accesstoken = mapbox_token,
    #margin = {t: 0, b: 0},
    zoom=3, 
    center = {"lat": 37.0902, "lon": -95.7129}, 
    ),
    width = 1200, 
    height = 800 )

layout.update(updatemenus=list([
    dict(x=0,
         y=1,
         xanchor='left',
         yanchor='middle',
         buttons=list([
             dict(
                 args=['visible', [True, False, False, False]],
                 label='Total Cases per 100,000',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, True, False, False]],
                 label='Percent of Predicted Deaths',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, False, True, False]],
                 label='New Cases per 100,000',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, False, False, True]],
                 label='New Deaths per 100,000',
                 method='restyle'
                )
            ]),
        )]))
fig=go.Figure(data = maps, layout=layout)

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter

