# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:56:51 2020

@author: Cole Fitzpatrick
"""

import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import scipy

def create_connection(db_file):
    """ create a database connection to the covid db """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as error:
        print(error)

#change this to your file path
covid_file = 'C:\Python\colefitzpatrick_python\STAT535\data3.db'
conn = create_connection(covid_file)

def populate_table(xls_file, sheet, conn, table_name):
    """ populates a db table with data from xls_file """

    xls_df = pd.read_excel(xls_file, sheet_name = sheet)
    xls_df.to_sql(table_name, conn, if_exists="append", index=False)

#Just need to run this once if you're saving the file locally, comment it out once you've done that
#populate_table("owid-covid-data.xlsx", "Sheet1", conn, "alldata")

c = conn.cursor()

c.execute("SELECT a.location, a.date, a.new_deaths_smoothed, (select new_cases_smoothed from alldata where location = a.location and date = substr(a.date_1, 1,10)) as new_cases_smoothed from alldata a where iso_code in ('CAN','CHN','BRA','GBR','DEU','FRA','IND','ITA','JPN','USA') and date between '2020-08-01' and '2020-10-31'")

#here's the part that isn't working
#d = ('substr(a.date_10, 1,10)',)
c.execute("SELECT a.location, a.date, a.new_deaths_smoothed, (select new_cases_smoothed from alldata where location = a.location and date = ?) as new_cases_smoothed from alldata a where iso_code in ('CAN','CHN','BRA','GBR','DEU','FRA','IND','ITA','JPN','USA') and date between '2020-08-01' and '2020-10-31'")

new_cases = []
new_deaths = []
for r in c.fetchall():
    new_cases.append(r[3])
    new_deaths.append(r[2])
    #print((r[0], r[1], r[2], r[3]))

slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(new_cases, new_deaths)
r_sq = r_value**2

r = 10
ax = sns.scatterplot(x=new_cases,y=new_deaths,edgecolor=None, s=3)
ax.set_xlabel("New Cases " + str(r) + " Day(s) Ago, $R^2$ = " + str(round(r_sq,3)))
ax.set_ylabel("New Deaths")
ax.set_title(str(r) + ' day lag')
plt.savefig(str(r) + 'daylag.png', dpi=600)
plt.show()



