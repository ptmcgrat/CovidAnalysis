import pandas as pd
import pdb, json
import plotly.express as px
from urllib.request import urlopen

herd_immunity = 0.7

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

fig = px.choropleth(all_dt, geojson=counties, locations='countyFIPS', color='Total Cases per 100,000',
					color_continuous_scale="Viridis",
					range_color=(0, 4000),
					scope="usa", hover_data=['PopulationID', '#Alive', 'CurrentCases', 'CurrentDeaths', 'PredictedDied'],
					labels = {'PopulationID':'County Name', '#Alive': 'Total Population', 'CurrentCases':'Total Positives','CurrentDeaths':'Actual Covid Deaths', 'PredictedDied': 'Predicted Covid Deaths'}
                  )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

fig = px.choropleth(all_dt, geojson=counties, locations='countyFIPS', color='Percent of Predicted Deaths',
					color_continuous_scale="Viridis",
					range_color=(0, 50),
					scope="usa", hover_data=['PopulationID', '#Alive', 'CurrentCases', 'CurrentDeaths', 'PredictedDied'],
					labels = {'PopulationID':'County Name', '#Alive': 'Total Population', 'CurrentCases':'Total Positives','CurrentDeaths':'Actual Covid Deaths', 'PredictedDied': 'Predicted Covid Deaths'}
                  )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

fig = px.choropleth(all_dt, geojson=counties, locations='countyFIPS', color='New Cases per 100,000',
					color_continuous_scale="Viridis",
					range_color=(0, 500),
					scope="usa", hover_data=['PopulationID', '#Alive', 'CurrentCases', 'DeltaCases', 'CurrentDeaths', 'PredictedDied'],
					labels = {'PopulationID':'County Name', '#Alive': 'Total Population', 'CurrentCases':'Total Positives','DeltaCases': 'New Cases (weekly)', 'CurrentDeaths':'Actual Covid Deaths', 'PredictedDied': 'Predicted Covid Deaths'}
                  )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

fig = px.choropleth(all_dt, geojson=counties, locations='countyFIPS', color='New Deaths per 100,000',
					color_continuous_scale="Viridis",
					range_color=(0, 50),
					scope="usa", hover_data=['PopulationID', '#Alive', 'CurrentCases', 'DeltaCases', 'CurrentDeaths', 'DeltaDeaths', 'PredictedDied'],
					labels = {'PopulationID':'County Name', '#Alive': 'Total Population', 'CurrentCases':'Total Positives','DeltaCases': 'New Cases (weekly)', 'CurrentDeaths':'Actual Covid Deaths', 'DeltaDeaths': 'New Deaths (weekly)', 'PredictedDied': 'Predicted Covid Deaths'}
                  )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

fig = px.choropleth(all_dt, geojson=counties, locations='countyFIPS', color='Predicted IFR',
					color_continuous_scale="Viridis",
					range_color=(0, 2),
					scope="usa", hover_data=['PopulationID', '#Alive', 'CurrentCases', 'DeltaCases', 'CurrentDeaths', 'PredictedDied'],
					labels = {'PopulationID':'County Name', '#Alive': 'Total Population', 'CurrentCases':'Total Positives','DeltaCases': 'New Cases (weekly)', 'CurrentDeaths':'Actual Covid Deaths', 'PredictedDied': 'Predicted Covid Deaths'}
                  )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
