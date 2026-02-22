# main.py

# import libraries

# import libraries to conduct eda
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# import scipy for statistical analysis in eda
#!pip install scipy
from scipy import stats

# import re to help with wildmatch for column name standardization
#import re

# import datetime to set timestamp on pdf report
from datetime import datetime

# import additional libraries to support ai generated code

# install pdfplumber
#!pip install pdfplumber -q

 # import pdfplumber and os to help import and transform data files
#import pdfplumber
#import os

# import fpdf for pdf generation
#!pip install fpdf
#from fpdf import FPDF

#!pip install PyPDF2
#import PyPDF2

print("All required libraries installed")

# data file names 

data_file_hurr = "../data/ibtracs.NA.list.v04r01.csv"

data_file_gas = "../data/gas_coordinates.csv"

data_file_coast = "../data/Gulf_Coast_Coords.csv"

# import file loading functions
from file_load import df_import

hurr_data = df_import(data_file_hurr)

gas_data = df_import(data_file_gas)

coast_pt_data = df_import(data_file_coast)

# import data cleaning functions
from clean import *

# Clean hurricane data and generate data frames for cleaned hurricane data, list of hurricanes, and summary list of hurricanes with maximum storm category observed
# Generates data frames with ALL data and a set of filtered data frames for "recent" (2022-2025)
hurr_data_redux, hurr_list, hurr_sum_list, hurr_data_redux_rec, hurr_list_rec, hurr_sum_list_rec= hurr_clean(hurr_data)

# Clean gas station data and generate data frame for cleaned gas station data
gas_data_redux = gas_clean(gas_data)

# Import coastal coordinates for visualizations


# Run visualizations

from eda_visuals import *

# Hurricane Overview Visuals
hurr_visuals(hurr_sum_list)

hurr_visuals(hurr_sum_list_rec)

# Gas Overview Visuals
gas_visuals(gas_data_redux)

# Hurricane Tracks Visuals

from hurr_tracks_viz import *

# Season Survey
hurr_tracks_season(hurr_data_redux)

# Single Hurricane Track
hurr_tracks_single(hurr_data_redux, coast_pt_data)

# Compare Hurricane Tracks
hurr_tracks_compare(hurr_data_redux, coast_pt_data)