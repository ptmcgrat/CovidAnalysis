import argparse, pdb
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils.utils import convertAgeGroupToTuple
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline

# DATA SOURES
# Covid and total death by age/state data comes from https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Sex-Age-and-S/9bhg-hcku
cdc_reported_2020deaths = 'https://data.cdc.gov/api/views/9bhg-hcku/rows.csv?accessType=DOWNLOAD'
#https://www.health.ny.gov/statistics/vital_statistics/2017/table31c.htm
total_NYC_deaths = 53806
# https://github.com/nychealth/coronavirus-data
total_predicted_NYC_covid_deaths = 'https://raw.githubusercontent.com/nychealth/coronavirus-data/master/summary.csv'
#OUTPUT FILES
outfile_allstates = 'CreatedData/RelativeCovidRiskNormalDeath.csv'

NYC_prevalence = 0.25 # Cuomo twitter

dt = pd.read_csv(cdc_reported_2020deaths).fillna(0)
dt = dt[(dt.Sex.isin(['Male', 'Female']))][['State', 'Data as of', 'Age group', 'Sex', 'COVID-19 Deaths', 'Total Deaths']]

# Just look at NYC and United States
dt = dt[dt.State.isin(['United States', 'New York City'])]
dt['CovidToTotalRate'] = dt['COVID-19 Deaths']/dt['Total Deaths'].apply(max, args = [1])
dt['Age'] = dt['Age group'].map(convertAgeGroupToTuple).map(np.mean)
dt = dt.convert_dtypes() #Make columns int now that we removed the NA values

nyc_dt = pd.read_csv(total_predicted_NYC_covid_deaths, names=['Type','Number'], header=None, index_col = 0)
#pdb.set_trace()

confirmed_deaths = int(nyc_dt.loc['NYC_CONFIRMED_DEATH_COUNT','Number'])
probable_deaths = int(nyc_dt.loc['NYC_PROBABLE_DEATH_COUNT','Number'])

#Use age range of US. Lots of olds probably missed from nursing homes:
#https://www1.nyc.gov/assets/doh/downloads/pdf/imm/covid-19-deaths-confirmed-probable-weekly-05072020.pdf

sns.lineplot(data = dt, x = 'Age', y = 'CovidToTotalRate', hue = 'State')
plt.show()		

predicted_risk = dt[dt.State == 'United States'].groupby(['Age group','Age']).sum().reset_index()
total_us_deaths = predicted_risk.sum()['Total Deaths']
covid_us_deaths = predicted_risk.sum()['COVID-19 Deaths']
predicted_risk['Normalized NYC Total'] = (predicted_risk['Total Deaths']/total_us_deaths*total_NYC_deaths)
predicted_risk['Normalized NYC Covid Confirmed'] = (predicted_risk['COVID-19 Deaths']/covid_us_deaths*confirmed_deaths/NYC_prevalence)
predicted_risk['Normalized NYC Covid Probable'] = (predicted_risk['COVID-19 Deaths']/covid_us_deaths*(confirmed_deaths + probable_deaths)/NYC_prevalence)
predicted_risk['ConfirmedCovidToNormal'] = predicted_risk['Normalized NYC Covid Confirmed']/predicted_risk['Normalized NYC Total']
predicted_risk['ProbableCovidToNormal'] = predicted_risk['Normalized NYC Covid Probable']/predicted_risk['Normalized NYC Total']
predicted_risk = predicted_risk.sort_values('Age')

RR_confirmed_interp = interp1d(predicted_risk['Age'], predicted_risk['ConfirmedCovidToNormal'], kind ='linear')
RR_probable_interp = interp1d(predicted_risk['Age'], predicted_risk['ProbableCovidToNormal'], kind='linear')

t_data = []
for age in range(101):
	t_data.append({'Age':age, 'RR confirmed': float(RR_confirmed_interp(min(age,92))), 'RR probable': float(RR_probable_interp(min(age,92)))})
out_data = pd.DataFrame(t_data)

sns.lineplot(data = out_data, x = 'Age', y = 'RR confirmed')
sns.lineplot(data = out_data, x = 'Age', y = 'RR probable')

sns.scatterplot(data = predicted_risk, x = 'Age', y = 'ConfirmedCovidToNormal')
sns.scatterplot(data = predicted_risk, x = 'Age', y = 'ProbableCovidToNormal')
plt.show()

nd_dt = pd.DataFrame(columns = ['Age', 'IFR_Confirmed', 'IFR_Probable', 'NDR', 'ExpYearsLeft'])
normal_deaths = pd.read_excel('https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/NVSR/68_07/Table01.xlsx', skiprows = [0])
count = 0
for age in range(0,101):
	normal_prob_dying = normal_deaths.loc[min(age+1,100),'Probability of dying between ages x and x + 1']
	expected_years_left = normal_deaths.loc[min(age+1,100),'Expectation of life at age x']
	t_data = {'Age': int(age), 'IFR_Confirmed': float(RR_confirmed_interp(min(age,92)))*float(normal_prob_dying),'IFR_Probable': float(RR_probable_interp(min(age,92)))*float(normal_prob_dying), 'NDR':float(normal_prob_dying), 'ExpYearsLeft': float(expected_years_left)}
	nd_dt.loc[count] = t_data
	count += 1
nd_dt = nd_dt.convert_dtypes()
nd_dt.set_index('Age')
sns.lineplot(data = nd_dt, x = 'Age', y = 'IFR_Probable')
plt.show()
nd_dt.to_csv(outfile_allstates)
pdb.set_trace()
