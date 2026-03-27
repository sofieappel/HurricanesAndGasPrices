# main_modeling.py

# import libraries

# import libraries 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import os

# import for distance calculations
#pip install geopy
from geopy import distance
import math

# import scipy for statistical analysis 
#!pip install scipy
from scipy import stats

# import datetime 
from datetime import datetime, timedelta, date, time

print("All required libraries installed")

# data file names

data_file_hurr = "../data/ibtracs.NA.list.v04r01.csv"

data_file_gas = "../data/aaa_fl_metros_wayback_2022_2025.csv"
#"../data/gas_coordinates.csv"

data_file_coast = "../data/Gulf_Coast_Coords.csv"

data_file_metro_loc = "../data/gas_coordinates.csv"

# import file loading functions
from file_load import *

# import data files
hurr_file_chk = input('Is hurricane data file downloaded to data folder? (y/n) ')
if hurr_file_chk == 'y':
    hurr_data = df_import(data_file_hurr)
else:
    url = 'https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv'
    hurr_data = pd.read_csv(url)

hurr_data.name = 'hurr_data'

gas_data = df_import(data_file_gas)
gas_data.name = 'gas_data'

coast_pt_data = df_import(data_file_coast)

metro_loc_data = coord_import(data_file_metro_loc)

# List metro areas of interest
# all FL cities selected to represent the perimeter

#metro_all = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral', 'Miami','West Palm Beach-Boca Raton','Melbourne-Titusville','Daytona Beach','Jacksonville']

# import data cleaning functions
from clean import *

# Clean hurricane data and generate data frames for cleaned hurricane data, list of hurricanes, and summary list of hurricanes with maximum storm category observed
# Generates data frames with ALL data and a set of filtered data frames for "recent" (2022-2025)
hurr_data_redux, hurr_list, hurr_sum_list, hurr_data_redux_rec, hurr_list_rec, hurr_sum_list_rec, hurr_data_redux_rec_hur = hurr_clean(hurr_data)

# Name output data frames
hurr_data_redux.name = 'hurr_data_redux'
hurr_list.name = 'hurr_list'
hurr_sum_list.name = 'hurr_sum_list'
hurr_data_redux_rec.name = 'hurr_data_redux_rec'
hurr_list_rec.name = 'hurr_list_rec'
hurr_sum_list_rec.name = 'hurr_sum_list_rec'
hurr_data_redux_rec_hur.name = 'hurr_data_redux_rec_hur'

# Clean gas station data and generate data frame for cleaned gas station data
gas_data_redux = gas_clean(gas_data)
gas_data_redux.name = 'gas_data_redux'

# import model data functions
from model_data_prep import *

# additional formatting of hurricane data
hurr_mod_data = hurr_data_prep(hurr_data_redux_rec_hur)

storm_data, storm_model_data = mod_data_config(hurr_mod_data, gas_data_redux, metro_loc_data)