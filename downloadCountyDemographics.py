import requests, pdb, pathlib
import pandas as pd
from scipy.interpolate import interp1d

pathlib.Path('CreatedData').mkdir(parents=True, exist_ok=True) 


county_data = [] # Hold all data as a list before converting into Dataframe
non_FIPS_codes = set([3,7,11,14,43,52]) #https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696
regions = {'Northeast':['Maine', 'New Hampshire', 'Vermont', 'Massachusetts', 'Connecticut', 'Rhode Island', 'New York', 'Pennsylvania', 'New Jersey', 'Maryland', 'Delaware'],
                   'South':['West Virginia', 'Virginia', 'North Carolina', 'Tennessee', 'South Carolina', 'Georgia', 'Florida', 'Mississippi', 'Alabama', 'Louisiana', 'Arkansas'],
				   'Midwest':['Ohio', 'Indiana', 'Kentucky', 'Illinois', 'Michigan', 'Wisconsin', 'Iowa', 'Missouri', 'Minnesota', 'North Dakota', 'South Dakota', 'Kansas', 'Nebraska'],
				   'Southwest':['Texas', 'Oklahoma', 'New Mexico', 'Arizona'],
				   'Mountain':['Montana','Idaho','Colorado','Wyoming','Nevada','Utah'],
				   'Pacific':['Washington','Oregon','California','Alaska','Hawaii']}

# Download all data, one sstate at a time using stateFIPS codes
for i in range(1,57): # Download one state at a time
	if i in non_FIPS_codes:
		continue

	# Data taken from 2018 US Census projections https://www.census.gov/data/developers/data-sets/popest-popproj/popest.Vintage_2018.html
	url = 'https://api.census.gov/data/2018/pep/charagegroups?' #Base url
	url += 'get=AGEGROUP,POP,GEONAME,COUNTY,DATE_CODE' # Define data to get
	url += '&for=county:*&in=state:' + str(i).zfill(2) #Define level at county + projection = 2020
	url += '&key=fca419702072e954d2fcdfc05f372c437bc0ab6d'

	req = requests.get(url)
	if req.status_code == 500:
		for j in range(10):
			print('Rerequesting data for ' + str(i) + '. Attempt #' + str(j+2))
			req = requests.get(url)
			if req.status_code == 200:
				break
		if req.status_code != 200:
			print('Cant get data for ' + str(i))
			continue

	elif req.status_code != 200:
		pdb.set_trace()

	data = req.content.decode('utf-8').split('\n')[1:]
	for data in req.content.decode('utf-8').split('\n')[1:-1]:
		try:
			row_data = eval(data.rstrip(','))
		except SyntaxError:
			pdb.set_trace()
		age_group, population, county_name, county_FIPS, date_code = int(row_data[0]),int(row_data[1]), row_data[2], row_data[3], int(row_data[4])
		county_FIPS = str(i).zfill(2) + county_FIPS.zfill(3)
		state = county_name.split(', ')[1]
		try:
			region = [x[0] for x in regions.items() if state in x[1]][0]
		except IndexError:
			pdb.set_trace()
		try:
			t_data = {'AgeGroup':age_group, 'Population':population, 'County': county_name, 'countyFIPS': county_FIPS, 'State': str(state).zfill(2), 'stateFIPS': i, 'Region':region, 'Date_code': date_code}
		except IndexError:
			pdb.set_trace()
		county_data.append(t_data)

county_dt = pd.DataFrame(county_data)

# Check to make sure all county has predictions for time code 11
if county_dt.groupby(['County','State']).max()['Date_code'].min() != 11:
	print('Time code issue')
	pdb.set_trace()

if county_dt.groupby(['State']).max()['Date_code'].count() != 50:
	print('Not enough states')
	pdb.set_trace()

county_dt = county_dt[county_dt.Date_code == 11] # 7/1/2018
#Age group info here: https://api.census.gov/data/2018/pep/charagegroups/variables/AGEGROUP.json
summed_dt = county_dt[(county_dt.AgeGroup > 0) & (county_dt.AgeGroup < 19)].groupby(['County','State']).sum()['Population'].reset_index() #0 = Total, 31 = Median
compare_dt = pd.merge(county_dt[county_dt.AgeGroup == 0],summed_dt, on = ['County','State'])

if compare_dt[(compare_dt.Population_x != compare_dt.Population_y)].shape[0] != 0:
	print('Population sums dont agree')
	pdb.set_trace()

county_dt = county_dt[(county_dt.AgeGroup > 0) & (county_dt.AgeGroup < 19)]

all_data = []

county_dt['Age'] = county_dt['AgeGroup']*5 - 2.5
county_dt.loc[county_dt['Age']==87.5,'Population'] = county_dt[county_dt['Age']==87.5].Population/2
county_dt.loc[county_dt['Age']==87.5,'Age'] = 90

for county in county_dt.groupby('County').groups.keys():
	state = county_dt[county_dt.County == county].iloc[0].State
	region = county_dt[county_dt.County == county].iloc[0].Region
	countyFIPS = county_dt[county_dt.County == county].iloc[0].countyFIPS
	stateFIPS = county_dt[county_dt.County == county].iloc[0].stateFIPS

	ages = county_dt[county_dt.County == county].Age.to_list() + [100] # Add 100
	num_alive = (county_dt[county_dt.County == county].Population/5).to_list() + [0] # Add 100
	interp_population = interp1d(ages, num_alive, kind = 'linear')

	for age in range(0,101):
		people = int(interp_population(max(age,3))) 
		t_data = {'PopulationID': county, 'countyFIPS': countyFIPS, 'Level': 'County', 'stateFIPS':stateFIPS, 'State': state, 'Region': region, 'Country': 'United States of America', 'Continent': 'North America', 'Age': age, '#Alive': people}
		all_data.append(t_data)

demographics = pd.DataFrame(all_data, index = list(range(len(all_data))))


# Add state data
all_data = []
state_level = demographics[demographics.Level == 'County'].groupby(['State','Region','Age','stateFIPS']).sum()['#Alive'].reset_index()
for index, row in state_level.iterrows():
	state = row.State
	region = row.Region
	age = row.Age
	t_data = {'PopulationID': row.State, 'countyFIPS': '', 'Level': 'State', 'stateFIPS':row.stateFIPS, 'State': row.State, 'Region': row.Region, 'Country': 'United States of America', 'Continent': 'North America', 'Age': row.Age, '#Alive': row['#Alive']}
	all_data.append(t_data)
t_dt = pd.DataFrame(all_data, index = list(range(len(demographics), len(demographics) + len(all_data))))
demographics = demographics.append(t_dt)

"""
nyc_counties = [x + ' County, New York' for x in ['Bronx','Kings','New York','Queens','Richmond']]
li_counties = [x + ' County, New York' for x in ['Nassau','Suffolk']]
wr_counties = [x + ' County, New York' for x in ['Rockland', 'Westchester']]
nys_counties = [x + ' County, New York' for x in ['Albany','Allegany','Broome','Cattaraugus','Cayuga','Chautauqua','Chemung','Chenango','Clinton','Columbia','Cortland','Delaware',
								 'Dutchess','Erie','Franklin','Fulton','Genesee','Greene','Hamilton','Herkimer','Jefferson','Lewis','Livingston','Madison','Monroe',
								 'Montgomery','Niagara','Oneida','Onondaga','Ontario','Orange','Orleans','Oswego','Otsego','Putnam','Rensselaer','Saint Lawrence',
								 'Saratoga', 'Schenectady','Schoharie','Schuyler','Seneca','Steuben','Sullivan','Tioga','Tompkins','Ulster','Warren','Washington',
								 'Wayne','Wyoming','Yates']]

self._addGrouping('New York City', nyc_counties, 'Substate', 'New York', 'North America', 'United States of America')
self._addGrouping('Long Island', li_counties, 'Substate', 'New York', 'North America', 'United States of America')
self._addGrouping('Westchester/Rockland', wr_counties, 'Substate', 'New York', 'North America', 'United States of America')
self._addGrouping('Rest of NY', nys_counties, 'Substate', 'New York', 'North America', 'United States of America')
"""
demographics.to_csv('CreatedData/Demographics.csv')