# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 19:59:48 2020

@author: Cole Fitzpatrick
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import linear_model
import warnings


best_lag = []
warnings.filterwarnings("ignore")
df = pd.read_excel("owid-covid_pared.xlsx", sheet_name = "Sheet1")


"""pare down the data frame to only have the necessary columns"""

df = df[['iso_code','continent', 'location', 'date', 'new_cases_smoothed', 'new_deaths_smoothed']]

"""pare down the data frame further to only include the countries in the sample (Top 10 by GDP)"""

countries = ['CHN','USA', 'IND', 'JPN', 'DEU', 'RUS', 'IDN', 'BRA', 'GBR', 'FRA', 'MEX', 'ITA', 'TUR', 'KOR', 'SAU', 'CAN', 'IRN', 'ESP', 'AUS', 'THA', 'PAK', 'NGA', 'EGY', 'POL']  
df = df[df['iso_code'].isin(countries)]

"""pare down further to only include the last four months of data (July thru October 2020)"""
df['date'] = pd.to_datetime(df['date'], yearfirst=True)
df_copy2 = df[(df['date'] >= '2020-07-01') & (df['date'] <= '2020-10-31')]

"""add a column for the lag date that is n days before the date for that column"""

for loc in countries:
    df_copy = df_copy2[df_copy2.iso_code == loc]
    r2_values = []    
    for n in range(1,31):
        
        df = df_copy
        df['lag_date'] = df.date - pd.to_timedelta(n, unit='d')
        
        """copy the data frame to the master because we'll now be manipulating this one"""
        df_master = df
        
        """remove new cases from the left data frame since we'll want to take it from the right"""
        df = df[['iso_code', 'continent', 'location', 'date', 'new_deaths_smoothed','lag_date']]
        
        """join the two data frames and pare it down"""
        merged_df = pd.merge(df, df_master, how='left', left_on=['iso_code','lag_date'], right_on=['iso_code','date'])
        merged_df = merged_df[(merged_df['date_x'] >= '2020-08-01') & (merged_df['date_x'] <= '2020-10-31')]
        merged_df = merged_df[['iso_code', 'continent_x', 'location_x', 'date_x', 'new_deaths_smoothed_x','new_cases_smoothed']]
        merged_df = merged_df.rename(columns={"continent_x": "Continent", "location_x": "Country"})
        
    
        """running a simple linear regression to calculate and r-squared"""
        x_df = merged_df[['new_cases_smoothed']]
        y_df = merged_df[['new_deaths_smoothed_x']]
        lm = linear_model.LinearRegression()
        model = lm.fit(x_df,y_df)
        r_sq = round(lm.score(x_df,y_df),3)
        r2_values.append(r_sq)
                
        """plotting and saving the data"""
        if n < 10:
            days = '0' + str(n)
        else:
            days = str(n)
           
        ax = plt.figure()
        ax = sns.scatterplot(data=merged_df, x="new_cases_smoothed", y="new_deaths_smoothed_x", hue="Country", edgecolor=None, s=4)
        ax.set_xlabel("New Cases " + days + " Day(s) Prior, $R^2$ = " + str(round(r_sq,3)))
        ax.set_ylabel("Deaths on a Given Day")
        ax.set_title("COVID-19 Case and Death Correlation, " + days + ' day lag')
        ax.legend(loc='lower right')
        plt.savefig(loc + '_' + str(n) + 'daylag.png', dpi=600)
        
        print(n)
        print(r_sq)
    max_r = max(r2_values)
    max_lag_day = r2_values.index(max_r)
    best_lag.append(max_lag_day)

"""plotting the best lag day for all the calculated r2"""
r2_df = pd.DataFrame(best_lag, columns=['Best Lag Day'])       
ax = plt.figure()
ax = sns.histplot(data=r2_df, x="Best Lag Day",binwidth=3)
plt.savefig('cumulative_r2.png', dpi=600)    
