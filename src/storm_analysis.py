# storm_analysis.py

# import libraries

#import libraries to conduct eda
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import os

# import for distance calculations
from geopy import distance
import math

def data_select(hurr_data_redux, hurr_sum_list, gas_data):
    # List metro areas of interest
    # all FL cities selected to represent the perimeter

    metro_all = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral', 'Miami',
                 'West Palm Beach-Boca Raton', 'Melbourne-Titusville', 'Daytona Beach', 'Jacksonville']

    # East coast of FL
    metro_east = ['Miami', 'West Palm Beach-Boca Raton', 'Melbourne-Titusville', 'Daytona Beach', 'Jacksonville']

    # West coast of FL (exl panhandle)
    metro_west = ['Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral']

    # Panhandle of FL
    metro_ph = ['Pensacola', 'Tallahassee']

    # Gulf Coast of FL (West + Panhandle)
    metro_gulf = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral']

    hurr_seas = int(input('Enter target hurricane season (year): '))

    if hurr_seas < 2022:
        hurr_gas = 0
        chk1 = input('No gas data exists for this season, continue? (y/n) ')
        if chk1 == 'n':
            print('Not continuing')
    else:
        hurr_gas = 1
        print(hurr_sum_list[['NAME','MAX CAT','STORM DURATION']][hurr_sum_list['SEASON'] == hurr_seas])

    hurr_name = input('Enter target hurricane name: ').upper()

    metro_sel = int(input(
        'Enter FL region of interest: 1 - All Coast, 2 - East Coast, 3 - Gulf Coast, 4 - West Coast, 5 - Panhandle '))

    match metro_sel:
        case 1:
            metro = metro_all
        case 2:
            metro = metro_east
        case 3:
            metro = metro_gulf
        case 4:
            metro = metro_west
        case 5:
            metro = metro_ph
        case _:
            print('Valid input not entered. Default to all')
            metro = metro_all

    hurr_data_select = hurr_data_redux[
        (hurr_data_redux['SEASON'] == hurr_seas) & (hurr_data_redux['NAME'] == hurr_name)]

    if hurr_data_select.shape[0] == 0:
        print(f'Requested storm ({hurr_seas} - {hurr_name}) not found')

    # Filter gas data to selected metro areas
    gas_data_select = gas_data[(gas_data['metro'].isin(metro))]

    # Convert date string to datetime format
    gas_data_select.loc[:, 'date'] = pd.to_datetime(gas_data_select['date'])

    return hurr_data_select, gas_data_select, metro, hurr_name, hurr_seas

def storm_overview(hurr_data_select, gas_data_select, metro, gc_data, hurr_name, hurr_seas, metro_loc_data):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd
    from datetime import datetime, timedelta

    # Extract storm start and end dates
    storm_start_date = hurr_data_select['ISO_TIME'].min()
    storm_end_date = hurr_data_select['ISO_TIME'].max()

    plt.figure(figsize=(7, 7))
    sns.scatterplot(
        data=hurr_data_select,
        x='USA_LON',
        y='USA_LAT', size='USA_SSHS', hue='USA_SSHS', palette='crest')
    plt.plot(gc_data['LON'], gc_data['LAT'], color='red', label='Data 2', linestyle='--')
    plt.title(f'{hurr_name} ({storm_start_date} - {storm_end_date})')
    plt.show()

    # Plot NOAA Distance to Land Calculations (for any land in any direction - all continents and any islands larger than 1400 km^2)
    plt.figure(figsize=(20, 10))
    sns.lineplot(data=hurr_data_select, x='ISO_TIME', y='DIST2LAND', errorbar=None)
    plt.title(f'Distance to Land (NOAA Calc) for Storm {hurr_name} in {hurr_seas}')
    plt.xlabel('Date')
    plt.ylabel('Distance to Land (km)')
    plt.show()

    # Plot time history of storm category (SSHS)
    plt.figure(figsize=(20, 10))
    sns.lineplot(data=hurr_data_select, x='ISO_TIME', y='USA_SSHS', errorbar=None)
    plt.title(f'Storm Category (SSHS) for Storm {hurr_name} in {hurr_seas}')
    plt.xlabel('Date')
    plt.ylabel('Storm Category')
    plt.show()

    # Plot storm wind speed and show applicable storm category (SSHS)
    plt.figure(figsize=(20, 10))
    p1 = sns.lineplot(data=hurr_data_select, x='ISO_TIME', y='USA_WIND', errorbar=None)
    plt.title(f'Wind Speed (kts) for Storm {hurr_name} in {hurr_seas}')
    plt.xlabel('Date')
    plt.ylabel('Storm Wind Speed (kts)')

    p1.axhline(64, color='blue', linestyle='--', linewidth=2)
    p1.text(x=storm_start_date, y=64 + 0.1, s=f"Cat 1 (64-82 kts)", color='black', va='bottom', ha='center')

    p1.axhline(83, color='green', linestyle='--', linewidth=2)
    p1.text(x=storm_start_date, y=83 + 0.1, s=f"Cat 2 (83-95 kts)", color='black', va='bottom', ha='center')

    p1.axhline(96, color='orange', linestyle='--', linewidth=2)
    p1.text(x=storm_start_date, y=96 + 0.1, s=f"Cat 3 (96-112 kts)", color='black', va='bottom', ha='center')

    p1.axhline(113, color='red', linestyle='--', linewidth=2)
    p1.text(x=storm_start_date, y=113 + 0.1, s=f"Cat 4 (113-136 kts)", color='black', va='bottom', ha='center')

    p1.axhline(137, color='darkred', linestyle='--', linewidth=2)
    p1.text(x=storm_start_date, y=137 + 0.1, s=f"Cat 5 (137+ kts)", color='black', va='bottom', ha='center')
    plt.show()

    gas_data_storm = gas_data_select[
        (gas_data_select['date'] >= storm_start_date) & (gas_data_select['date'] <= storm_end_date)]

    # Plot gas price during storm for selected metro
    plt.figure(figsize=(20, 10))
    sns.lineplot(data=gas_data_storm, x='date', y='regular', hue='metro', errorbar=None)
    plt.title(f'Regular Gas Price for Storm {hurr_name} in {hurr_seas}')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

    # Set offset dates to look at gas prices before and after a storm
    storm_start_date_offset = storm_start_date + timedelta(days=-14)
    storm_end_date_offset = storm_end_date + timedelta(days=14)

    gas_data_storm_offset = gas_data_select[
        (gas_data_select['date'] >= storm_start_date_offset) & (gas_data_select['date'] <= storm_end_date_offset)]

    # Plot gas prices for two weeks before and after storm as well as during

    plt.figure(figsize=(20, 10))
    sns.lineplot(data=gas_data_storm_offset, x='date', y='regular', hue='metro', errorbar=None)
    # sns.lineplot(data=gas_data_select, x='date', y='regular', hue='metro')
    plt.title(f'Regular Gas Price for Storm {hurr_name} in {hurr_seas}')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')

    plt.axvspan(storm_start_date, storm_end_date, alpha=0.3)
    plt.show()

    metro_analysis(metro_loc_data, hurr_data_select, gas_data_select, metro, storm_start_date, storm_end_date, hurr_name)

def metro_analysis(metro_loc_data, hurr_data_select, gas_data_select, metro, storm_start_date, storm_end_date, hurr_name):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    # import for distance calculations
    from geopy import distance
    import math

    # Pull location data for metro areas (single point)
    metro_loc_select = metro_loc_data[(metro_loc_data['metro'].isin(metro))]

    gas_data_storm = gas_data_select[
        (gas_data_select['date'] >= storm_start_date) & (gas_data_select['date'] <= storm_end_date)]

    for M in metro_loc_select['metro']:
        print(M)
        
        tie_in = []

        luc = metro_loc_select['metro'] == M

        landpoint_lat = metro_loc_select.loc[luc, 'lat']
        landpoint_lon = metro_loc_select.loc[luc, 'lng']

        point1 = (landpoint_lat.item(), landpoint_lon.item())

        d = len(hurr_data_select)
        dist_date = [] * d
        dist_dist = [] * d

        # Set fixed point array
        start = [point1] * d
        start_df = pd.DataFrame(start)
        start_array = start_df.to_numpy()

        # set data frame to catch distance data
        tie_in = hurr_data_select[['ISO_TIME', 'USA_LAT', 'USA_LON']].reset_index(drop=True)
        # print(tie_in.head())
        # tie_in.shape

        finish = hurr_data_select[['USA_LAT', 'USA_LON']]
        results = [] * d

        finish_array = finish.to_numpy()

        for i in range(len(hurr_data_select)):
            dist = (distance.distance(start_array[i], finish_array[i]).km)
            results.append(dist)

        results_df = pd.DataFrame(results, columns=['dist'])
        results_df.head()
        results_df.shape

        tie_in['dist'] = results_df

        print(tie_in)

        plt.figure(figsize=(20, 20))
        plt.subplot(2, 1, 1)
        # Plot distance to metro for storm
        sns.lineplot(data=tie_in, x='ISO_TIME', y='dist', errorbar=None)
        plt.title(f'Distance to {M} & Regular Gas Price for Storm {hurr_name}')
        plt.xlabel(' ')
        plt.xticks(fontsize=8)
        plt.ylabel('Distance to Land (km)')

        plt.subplot(2, 1, 2)
        # Plot gas price during storm for selected metro
        sns.lineplot(data=gas_data_storm, x='date', y='regular', hue='metro', errorbar=None)
        #plt.title(f'Regular Gas Price for Storm {hurr_name}')
        plt.xlabel('Date')
        plt.xticks(fontsize=8)
        plt.ylabel('Gas Price (Regular)')
        plt.show()

def map_plot(metro_loc_data, metro_all, coast_pt_data):
    metro_select = metro_loc_data[(metro_loc_data['metro'].isin(metro_all))]

    plt.figure(figsize=(10, 10))
    sns.scatterplot(data=metro_select, x='lng', y='lat')
    plt.plot(coast_pt_data['LON'], coast_pt_data['LAT'], color='red', label='Data 2', linestyle='--')

    for index, row in metro_select.iterrows():
        if row['lng'] < -82:
            plt.annotate(
                row['metro'],
                (row['lng'], row['lat']),
                textcoords="offset points",
                fontsize=7,
                xytext=(-15, 5),
                ha='center')
        else:
            plt.annotate(
                row['metro'],
                (row['lng'], row['lat']),
                textcoords="offset points",
                fontsize=7,
                xytext=(10, 5),
                ha='center')
    plt.title(f'Selected Florida Metro Areas for Gas Data Analysis')
    plt.show()

def rel_plot(hurr_seas, hurr_name, metro_nm, metro_loc_data, hurr_data_redux, gas_data_redux):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from datetime import datetime, timedelta
    
    metro_loc_select = []
    hurr_data_select = []
    gas_data_select = []
    gas_data_storm = []
    tie_in = []

    metro_loc_select = metro_loc_data[(metro_loc_data['metro'] == metro_nm)]

    hurr_data_select = hurr_data_redux[
        (hurr_data_redux['SEASON'] == hurr_seas) & (hurr_data_redux['NAME'] == hurr_name)]

    # Filter gas data to selected metro areas
    gas_data_select = gas_data_redux[(gas_data_redux['metro'] == metro_nm)]

    # Convert date string to datetime format
    gas_data_select.loc[:, 'date'] = pd.to_datetime(gas_data_select['date'])

    # Extract storm start and end dates
    storm_start_date = hurr_data_select['ISO_TIME'].min()
    storm_end_date = hurr_data_select['ISO_TIME'].max()

    # Gas data during storm
    gas_data_storm = gas_data_select[
        (gas_data_select['date'] >= storm_start_date) & (gas_data_select['date'] <= storm_end_date)]
    gas_data_storm.loc[:, 'date_time_key'] = gas_data_storm['date'] + timedelta(hours=12, minutes=0, seconds=0)

    # Set metro location / coords
    luc = metro_loc_select['metro'] == metro_nm

    landpoint_lat = metro_loc_select.loc[luc, 'lat']
    landpoint_lon = metro_loc_select.loc[luc, 'lng']

    point1 = (landpoint_lat.item(), landpoint_lon.item())

    d = len(hurr_data_select)
    dist_date = [] * d
    dist_dist = [] * d

    start = [point1] * d
    start_df = pd.DataFrame(start)
    start_array = start_df.to_numpy()

    # set data frame to catch distance data
    tie_in = pd.DataFrame(
        hurr_data_select[['ISO_TIME', 'DATE', 'USA_LAT', 'USA_LON', 'USA_WIND', 'STORM_SPEED']].reset_index(drop=True))
    tie_in.rename(columns={'DATE': 'date'}, inplace=True)
    tie_in['date_time_key'] = tie_in['ISO_TIME']

    # Storm location
    finish = hurr_data_select[['USA_LAT', 'USA_LON']]
    results = [] * d

    finish_array = finish.to_numpy()

    # Iterate to calculate storm distance from metro point
    for i in range(len(hurr_data_select)):
        dist = (distance.distance(start_array[i], finish_array[i]).km)
        results.append(dist)

    results_df = pd.DataFrame(results, columns=['dist'])
    results_df.head()
    results_df.shape

    tie_in['dist'] = results_df

    # Plot generation
    # Plot of hurricane parameters and avg gas prices to look at trends
    fig, axs = plt.subplots(3, 1, figsize=(8, 10))
    fig.subplots_adjust(hspace=0.5, top=0.9, bottom=0.1, left=0.1, right=0.9)  # wspace=0.3,
    fig.suptitle(f'Hurricane {hurr_name.capitalize()} ({hurr_seas}) and {metro_nm} Gas Prices', fontsize=16,
                 fontweight='bold')

    # Subplot 1: Storm distance from Metro and Avg Gas Prices (Reg)
    ax1 = axs[0]
    ax2 = ax1.twinx()
    sns.scatterplot(data=tie_in, x='ISO_TIME', y='dist', ax=ax1, label = 'Distance')
    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax2)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax2, label = 'Avg gas price (reg)')
    ax1.set_xlabel('Date')
    ax1.tick_params(axis='x', labelsize=8)
    ax1.set_ylabel(f'Distance to Metro Area (km)')
    ax2.set_ylabel('Gas Price ($/gal)')
    plt.title(f'Distance from Hurricane to Metro Area (km) & Average Regular Gas Prices', fontsize=14)
    axs[0].legend(loc='upper right')

    # Subplot 2: Storm Wind Speed and Avg Gas Prices (Reg)
    ax3 = axs[1]
    ax4 = ax3.twinx()
    sns.scatterplot(data=tie_in, x='ISO_TIME', y='USA_WIND', color='green', ax=ax3, label = 'Wind speed')
    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax4)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax4, label = 'Avg gas price (reg)')
    ax3.set_xlabel('Date')
    ax3.tick_params(axis='x', labelsize=8)
    ax3.set_ylabel(f'Wind Speed (kts)')
    ax4.set_ylabel('Gas Price ($/gal)')
    plt.title(f'Hurricane Wind Speed (kts) & Average Regular Gas Prices', fontsize=14)
    axs[1].legend(loc='upper right')

    # Subplot 3: Storm Speed of Travel and Avg Gas Prices (Reg)
    ax5 = axs[2]
    ax6 = ax5.twinx()
    sns.scatterplot(data=tie_in, x='ISO_TIME', y='STORM_SPEED', color='purple', ax=ax5, label = 'Storm speed')
    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax6)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax6, label = 'Avg gas price (reg)')
    ax5.set_xlabel('Date')
    ax5.tick_params(axis='x', labelsize=8)
    ax5.set_ylabel(f'Storm Speed (kts)')
    ax6.set_ylabel('Gas Price ($/gal)')
    plt.title(f'Hurricane Storm Speed (kts) & Average Regular Gas Prices', fontsize=14)
    axs[2].legend(loc='upper right')

    plt.show()

    # Plot of Metro Gas Prices during Hurricane
    # Subplot 1: Average Gas Prices (Regular, Mid, and Premium) during Hurricane duration
    fig1, axs = plt.subplots(2, 1, figsize=(8, 10))
    fig1.subplots_adjust(hspace=0.5, top=0.9, bottom=0.1, left=0.1, right=0.9)  # wspace=0.3,
    fig1.suptitle(f'{metro_nm} Gas Prices during Hurricane {hurr_name}', fontsize=16, fontweight='bold')

    ax = axs[0]
    ax.set_title(f'Metro Average Gas Prices during Hurricane', fontsize=14)
    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'], color='orange', ax=ax, label = 'Regular')

    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['mid'], color='blue', ax=ax)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['mid'], color='blue', ax=ax, label = 'Mid')

    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['premium'], color='red', ax=ax)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['premium'], color='red', ax=ax, label = 'Premium')

    ax.set_xlabel('Date')
    ax.tick_params(axis='x', labelsize=8)
    axs[0].legend(loc='upper right')

    ax.set_ylabel('Gas Price ($/gal)')

    # Subplot : Changes in Average Gas Prices (Regular, Mid, and Premium) during Hurricane duration
    # Change is taken with respect to the gas price on the first day of storm data
    bl_reg = gas_data_storm['regular'].iat[0].item()
    bl_mid = gas_data_storm['mid'].iat[0].item()
    bl_pre = gas_data_storm['premium'].iat[0].item()

    ax1 = axs[1]
    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'] - bl_reg, color='orange',
                    ax=ax1)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['regular'] - bl_reg, color='orange', ax=ax1, label = 'Regular')

    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['mid'] - bl_mid, color='blue', ax=ax1)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['mid'] - bl_mid, color='blue', ax=ax1, label = 'Mid')

    sns.scatterplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['premium'] - bl_pre, color='red', ax=ax1)
    sns.lineplot(data=gas_data_storm, x='date_time_key', y=gas_data_storm['premium'] - bl_pre, color='red', ax=ax1, label = 'Premium')

    ax1.set_xlabel('Date')
    ax1.tick_params(axis='x', labelsize=8)

    ax1.set_ylabel('Change in Gas Price ($/gal)')
    ax1.set_title(f'Changes in Average Gas Prices Changes during Hurricane', fontsize=14)
    axs[1].legend(loc='upper right')

    plt.show()
