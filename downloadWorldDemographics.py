import pandas as pd
import numpy as np
from utils.utils import convertAgeGroupToTuple
import pdb, pathlib
from scipy.interpolate import interp1d

pathlib.Path('CreatedData').mkdir(parents=True, exist_ok=True) 

#https://population.un.org/wpp/Download/Standard/Population/
world_demographics_file = 'https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/EXCEL_FILES/1_Population/WPP2019_POP_F07_1_POPULATION_BY_AGE_BOTH_SEXES.xlsx' 
# https://en.wikipedia.org/wiki/ISO_3166-1_numeric

t_data = {}
all_data = []

dt = pd.read_excel(world_demographics_file, sheet_name = 'ESTIMATES', skiprows = 16)
dt = dt[(dt.Type == 'Country/Area') & (dt['Reference date (as of 1 July)'] == 2020)] # Use only countries and 2020 projections
dt = pd.melt(dt, id_vars = ['Region, subregion, country or area *','Country code', 'Parent code'], value_vars = [x for x in dt.columns if '-' in x] + ['100+'])
dt['Age'] = dt.variable.apply(convertAgeGroupToTuple).apply(np.mean)
dt['AgeRange'] = dt.variable.apply(convertAgeGroupToTuple).apply(np.diff).apply(np.mean)+1
dt['Population'] = dt['value']/dt['AgeRange']*1000

# read in continents file
#continents_dt = pd.read_csv('country-and-continent-codes-list-csv_csv.csv')
#continents_dt['Short_country'] = continents_dt.Country_Name.str.split(',', expand=True)[0]
#continents_dt = continents_dt[['Continent_Name','Short_country']]

all_data = []
for country in dt.groupby(['Region, subregion, country or area *']).groups.keys():
	country_code = dt[dt['Region, subregion, country or area *'] == country].iloc[0]['Country code']
	parent_code = dt[dt['Region, subregion, country or area *'] == country].iloc[0]['Parent code']
	ages = dt[dt['Region, subregion, country or area *'] == country].Age.to_list()
	num_alive = dt[dt['Region, subregion, country or area *'] == country].Population.to_list()
	interp_population = interp1d(ages, num_alive, kind = 'linear')

	for age in range(0,101):
		people = int(interp_population(max(age,2))) 
		t_data = {'PopulationID': country, 'country_code': country_code, 'Level': 'Country', 'continent_code':parent_code, 'Age': age, '#Alive': people}
		all_data.append(t_data)

demographics = pd.DataFrame(all_data, index = list(range(len(all_data))))
demographics.to_csv('CreatedData/WorldDemographics.csv')