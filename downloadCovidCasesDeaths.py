import pandas as pd
import datetime, pathlib

county_case_data = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'
county_death_data = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv'

# Get cases data
c_dt = pd.read_csv(county_case_data, dtype = {'countyFIPS':'str', 'stateFIPS':'str'})
c_dt['countyFIPS'] = c_dt.countyFIPS.str.zfill(5)
c_dt['stateFIPS'] = c_dt.stateFIPS.str.zfill(2)
c_dt = pd.melt(c_dt, id_vars = c_dt.columns[0:4], value_vars = c_dt.columns[4:], var_name = 'Date', value_name = 'Cases')

# Get death data
d_dt = pd.read_csv(county_death_data, dtype = {'countyFIPS':'str', 'stateFIPS':'str'})
d_dt['countyFIPS'] = d_dt.countyFIPS.str.zfill(5)
d_dt['stateFIPS'] = d_dt.stateFIPS.str.zfill(2)
d_dt = pd.melt(d_dt, id_vars = d_dt.columns[0:4], value_vars = d_dt.columns[4:], var_name = 'Date', value_name = 'Deaths')

dt = pd.merge(c_dt, d_dt, on = ['County Name', 'countyFIPS', 'State', 'stateFIPS', 'Date']).reset_index()

today = datetime.datetime.now() - datetime.timedelta(days = 1)
last_week = datetime.datetime.now() - datetime.timedelta(days = 8)
today = str(today.month) + '/' + str(today.day) + '/' + str(today.year)[2:]
last_week = str(last_week.month) + '/' + str(last_week.day) + '/' + str(last_week.year)[2:]


cases_dt = pd.merge(dt[dt.Date == today], dt[dt.Date == last_week][['countyFIPS','Cases','Deaths']], on = 'countyFIPS')
cases_dt['CurrentDeaths'] = cases_dt['Deaths_x']
cases_dt['CurrentCases'] = cases_dt['Cases_x']
cases_dt['DeltaDeaths'] = cases_dt['Deaths_x'] - cases_dt['Deaths_y']
cases_dt['DeltaCases'] = cases_dt['Cases_x'] - cases_dt['Cases_y']

cases_dt = cases_dt[cases_dt.columns[1:6].to_list() + cases_dt.columns[9:].to_list()]

pathlib.Path('CreatedData').mkdir(parents=True, exist_ok=True) 

cases_dt.to_csv('CreatedData/CovidCasesDeaths.csv')