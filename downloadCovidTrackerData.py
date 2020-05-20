import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pdb, pathlib

data = {}
data['GA'] = pd.read_html('https://covidtracking.com/data/state/georgia#historical', index_col = 0)[1].drop(columns=['Screenshots (EDT)','Total','Hospitalized'])
data['NY'] = pd.read_html('https://covidtracking.com/data/state/new-york#historical', index_col = 0)[1].drop(columns=['Screenshots (EDT)','Total','Hospitalized'])
data['NJ'] = pd.read_html('https://covidtracking.com/data/state/new-jersey#historical', index_col = 0)[1].drop(columns=['Screenshots (EDT)','Total','Hospitalized'])
data['US'] = pd.read_html('https://covidtracking.com/data/us-daily', index_col = 0)[0].drop(columns=['States Tracked', 'Total Tests', 'Pos + Neg'])


for key, dt in data.items():
	dt['Area'] = key
	dt.index = pd.to_datetime(dt.index)
	dt = dt.sort_index()
	dt = dt.iloc[-60:].fillna(0).convert_dtypes()
	dt['NewPositives'] = dt.Positive.diff(periods = 1)
	dt['NewNegatives'] = dt.Negative.diff(periods = 1)
	dt['NewDeaths'] = dt.Deaths.diff(periods = 1)

	dt = dt.fillna(0).convert_dtypes()

	dt['NewPositives_7'] = dt.NewPositives.rolling(7).mean()
	dt['NewNegatives_7'] = dt.NewNegatives.rolling(7).mean()
	dt['NewDeaths_7'] = dt.NewDeaths.rolling(7).mean()

	data[key] = dt


data['NY/NJ'] = data['NJ'].drop(['Area'], axis = 1).add(data['NY'].drop(['Area'], axis = 1))
data['NY/NJ']['Area'] = 'NY/NJ'
data['NonNY/NJ'] = data['US'].drop(['Area'], axis = 1).sub(data['NY/NJ'].drop(['Area'], axis = 1))
data['NonNY/NJ']['Area'] = 'NonNY/NJ'

a_dt = pd.DataFrame(columns = data['US'].columns)
for key, dt in data.items():
	a_dt = a_dt.append(dt)

a_dt['PercentPositive'] = a_dt['NewPositives_7']/(a_dt['NewPositives_7']+a_dt['NewNegatives_7'])

#x_values = list(range(60))
#sns.lineplot(x = x_values, y = data['US']['PercentPositive'].tolist())
#sns.lineplot(x = x_values, y = data['NYC']['PercentPositive'].tolist())
#sns.lineplot(x = x_values, y = data['NonNYC']['PercentPositive'].tolist())

sns.lineplot(data = a_dt, x = a_dt.index, y = 'PercentPositive', hue = 'Area')
plt.show()

sns.lineplot(data = a_dt, x = a_dt.index, y = 'NewPositives_7', hue = 'Area')
plt.show()

sns.lineplot(data = a_dt, x = a_dt.index, y = 'NewDeaths_7', hue = 'Area')
plt.show()

pathlib.Path('CreatedData').mkdir(parents=True, exist_ok=True) 
