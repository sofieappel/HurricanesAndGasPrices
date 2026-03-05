# main.py

# import libraries

# import libraries to conduct eda
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import os

# import for distance calculations
from geopy import distance
import math

# import scipy for statistical analysis in eda
#!pip install scipy
from scipy import stats

# import re to help with wildmatch for column name standardization
#import re

# import datetime to set timestamp on pdf report
from datetime import datetime, timedelta

print("All required libraries installed")

# data file names 

data_file_hurr = "../data/ibtracs.NA.list.v04r01.csv"

data_file_gas = "../data/aaa_fl_metros_wayback_2022_2025.csv"
#"../data/gas_coordinates.csv"

data_file_coast = "../data/Gulf_Coast_Coords.csv"

data_file_metro_loc = "../data/gas_coordinates.csv"

# import file loading functions
from file_load import df_import

# import data files
hurr_file_chk = input('Is hurricane data file downloaded to data folder? (y/n) ')
if hurr_file_chk == 'y':
    hurr_data = df_import(data_file_hurr)
    hurr_data.name = 'hurr_data'
else:
    url = 'https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv'
    hurr_data = pd.read_csv(url)

gas_data = df_import(data_file_gas)
gas_data.name = 'gas_data'

coast_pt_data = df_import(data_file_coast)

metro_loc_data = coord_import(data_file_metro_loc)

# import stats functions
from stats_look import *

# run stats on baseline data
# basic analysis on hurricane data
sum_stats(hurr_data)

# basic analysis on gas data
sum_stats(gas_data)

# import data cleaning functions
from clean import *

# Clean hurricane data and generate data frames for cleaned hurricane data, list of hurricanes, and summary list of hurricanes with maximum storm category observed
# Generates data frames with ALL data and a set of filtered data frames for "recent" (2022-2025)
hurr_data_redux, hurr_list, hurr_sum_list, hurr_data_redux_rec, hurr_list_rec, hurr_sum_list_rec , hurr_data_redux_rec_hur = hurr_clean(hurr_data)

# Name output data frames
hurr_data_redux.name = 'hurr_data_redux'
hurr_list.name = 'hurr_list'
hurr_sum_list.name = 'hurr_sum_list'
hurr_data_redux_rec.name = 'hurr_data_redux_rec'
hurr_list_rec.name = 'hurr_list_rec'
hurr_sum_list_rec.name = 'hurr_sum_list_rec'
hurr_data_redux_rec_hur.name = 'hurr_data_redux_rec_hur'

# List metro areas of interest
# all FL cities selected to represent the perimeter
metro_all = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral', 'Miami','West Palm Beach-Boca Raton','Melbourne-Titusville','Daytona Beach','Jacksonville']

# East coast of FL
metro_east = ['Miami','West Palm Beach-Boca Raton','Melbourne-Titusville','Daytona Beach','Jacksonville']

# West coast of FL (exl panhandle)
metro_west = ['Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral']

# Panhandle of FL
metro_ph = ['Pensacola', 'Tallahassee']

# Gulf Coast of FL (West + Panhandle)
metro_gulf = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral']


# Clean gas station data and generate data frame for cleaned gas station data
gas_data_redux = gas_clean(gas_data)
gas_data_redux.name = 'gas_data_redux'

# run stats on cleaned data
# basic analysis on cleaned hurricane data
sum_stats(hurr_data_redux)

# basic analysis on cleaned gas data
sum_stats(gas_data_redux)

# Run visualizations

from eda_visuals import *

# Hurricane Overview Visuals
hurr_visuals(hurr_sum_list)

hurr_visuals(hurr_sum_list_rec)

# Hurricane Stats Visuals
# All storms 2022-2025
stats_hurr_viz(hurr_data_redux_rec)

# All hurricanes 2022-2025
stats_hurr_viz(hurr_data_redux_rec_hur)

# Gas Overview Visuals
gas_visuals_ov(gas_data_redux, metro_all)

gas_visuals(gas_data_redux, metro_east)

gas_visuals(gas_data_redux, metro_gulf)

# Hurricane Tracks Visuals

from hurr_tracks_viz import *

# Season Survey
#hurr_tracks_season(hurr_data_redux)

# Single Hurricane Track
#hurr_tracks_single(hurr_data_redux, coast_pt_data)

# Compare Hurricane Tracks
#hurr_tracks_compare(hurr_data_redux, coast_pt_data)
from storm_analysis import *

map_plot(metro_loc_data, metro_all, coast_pt_data)

hurr_data_select, gas_data_select, metro, hurr_name, hurr_seas = data_select(hurr_data_redux, hurr_sum_list, gas_data_redux)

storm_overview(hurr_data_select, gas_data_select, metro, coast_pt_data, hurr_name, hurr_seas, metro_loc_data)


