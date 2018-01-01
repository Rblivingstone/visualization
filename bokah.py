#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 17:03:23 2017

@author: ryan
"""

from bokeh.io import output_file, show
from bokeh.layouts import widgetbox,column,row
from bokeh.models.widgets import RadioGroup, Button, Dropdown, Select
from bokeh.models import Range1d
from bokeh.plotting import figure, curdoc
import pandas as pd
import pickle
import re
import numpy as np


temp1 = pd.read_csv('Expenditures.csv')
temp2 = pd.read_csv('Taxes.csv')

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

trace = pickle.load(open('trace.pkl','rb'))
#%%

p1 = figure(x_range=[2005,2009], y_range=(0,1), title='Tax Rate Per Year')
p2 = figure(x_range=[2005,2009], y_range=(df['Data_Value'].min(),df['Data_Value'].max()),title='Expenditures on Cigarette Related Healthcare')
p3 = figure(title='Distribution of Savings (in Millions of $) Per 1% Increase in Tax Rate per Year')
lines = []
lines2 = []
hists = []
i = 0
line_dict = {}
height_dict ={}
x_start={}
x_end = {}
for state in df['LocationAbbr'].unique():
    line_dict[state] = i
    temp = df[df['LocationAbbr'] == state]
    amt = temp.iloc[4,10]
    hist, edges = np.histogram(np.random.choice((-trace)*amt,1000),density=True)
    x_start[state] = edges[0]
    x_end[state] = edges[-1]
    height_dict[state] = np.max(hist)
    lines.append(p1.line(temp['Year'],temp['tax']))
    lines2.append(p2.line(temp['Year'],temp['Data_Value']))
    hists.append(p3.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
        fill_color="#036564", line_color="#033649"))
    
    i+=1
    
for line in lines:
    line.glyph.line_alpha=0
for line in lines2:
    line.glyph.line_alpha=0
for hist in hists:
    hist.glyph.fill_alpha=0
    hist.glyph.line_alpha=0

menu = [(obj,str(line_dict[obj])) for obj in line_dict]
def callback(attr, old, new):
    p3.x_range.start=x_start[new]
    p3.x_range.end=x_end[new]
    p3.y_range.start=0
    p3.y_range.end=height_dict[new]
    lines[line_dict[old]].glyph.line_alpha=0
    lines[line_dict[new]].glyph.line_alpha = 1
    lines2[line_dict[old]].glyph.line_alpha=0
    lines2[line_dict[new]].glyph.line_alpha = 1
    hists[line_dict[old]].glyph.line_alpha=0
    hists[line_dict[new]].glyph.line_alpha=1
    hists[line_dict[old]].glyph.fill_alpha=0
    hists[line_dict[new]].glyph.fill_alpha=1
    
    
dropdown = Select(title="State",value='CA',options=list(df['LocationAbbr'].unique()))


#dropdown.  
dropdown.on_change('value',callback)
#dropdown.on_click(callback)
curdoc().add_root(column(dropdown,row(p1,p2),row(p3)))