#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 07:28:36 2017

@author: ryan
"""

import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import pymc3 as pm

temp1 = pd.read_csv('~/Documents/tobacco/Expenditures.csv')
temp2 = pd.read_csv('~/Documents/tobacco/Taxes.csv')

temp3 = temp2[(temp2['ProvisionDesc'] == 'Cigarette Tax ($ per pack)')]
tax = []
for obj in temp3['ProvisionValue']:
    try:
        tax.append(re.findall('^\d*[0-9](|.\d*[0-9]|,\d*[0-9])?$',obj)[0])
    except:
        tax.append(np.nan)
temp3['tax'] = tax
temp3['tax'] = temp3['tax'].astype('float64')
temp4 = temp3.groupby(['Year','LocationAbbr'])['tax'].mean().reset_index()
df = pd.merge(
                temp1[temp1['Variable']=='Total'],
                temp4,
                how='inner',
                on=['Year','LocationAbbr']
            )
df = df[['Year','LocationAbbr','Data_Value','tax']]
for state in df['LocationAbbr']:
    plt.plot(df[df['LocationAbbr']==state]['Year'],df[df['LocationAbbr']==state]['tax'])
    plt.title('Variation in Tobacco Tax By State')
    plt.ylabel('Tax ($ per pack)')
    plt.xlabel('Year')
plt.show()
for state in df['LocationAbbr']:
    plt.plot(df[df['LocationAbbr']==state]['Year'],df[df['LocationAbbr']==state]['Data_Value'])
    plt.title('Variation in Tobacco Tax By State')
    plt.ylabel('Expenditures (Millions of Dollars)')
    plt.xlabel('Year')
plt.show()

df['year_index'] = pd.factorize(df['Year'])[0]
df['state_index'] = pd.factorize(df['LocationAbbr'])[0]
df['tax'] = [obj if obj!=0 else 0.0001 for obj in df['tax']]
df['logtax'] = np.log(df['tax'])
df['logExpense'] = np.log(df['Data_Value'])
df.dropna(inplace=True)

with pm.Model() as model:
    state_fixed_effects=pm.Flat('State_Fixed', shape=len(df['LocationAbbr'].unique()))
    time_fixed_effects=pm.Flat('Time_Fixed',shape=len(df['Year'].unique()))
    tax_beta = pm.Flat('beta')
    lm = pm.Deterministic('mu',tax_beta*np.array(df['logtax'])+state_fixed_effects[np.array(df['state_index'])]+time_fixed_effects[np.array(df['year_index'])])
    sigma = pm.Flat('sigma')
    sigma2 = pm.Deterministic('sigma2',sigma**2)
    obs=pm.Normal('Observed', mu=lm, sd=sigma2, observed=df['logExpense'])
    trace = pm.sample(1000, tune=1000)
   
pm.traceplot(trace,varnames=['beta'])
plt.show()
