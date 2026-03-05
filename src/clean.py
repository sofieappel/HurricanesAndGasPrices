# clean.py

# hurr_data_clean

# hurricane data file is hurr_data

def hurr_clean(hurr_data):
    print(f"Cleaning {hurr_data.name}")
    
    import numpy as np
    import pandas as pd
    from datetime import datetime

    # Replace "NA" with "NATL" to eliminate confusion between North Atlantic (NA) and an indication of an empty cell or NA value
    hurr_data['BASIN'] = hurr_data['BASIN'].replace(np.nan, 'NATL')

    # Extract first row from data table which contains units
    hurr_units = pd.DataFrame(hurr_data.iloc[0,:])

    hurr_units.columns = ['Unit']

    print(hurr_units.head())
    print(hurr_units.shape)

    # Remove columns that are blank and used for data/reporting from other (international) weather monitoring agencies
    # Or has redundant data
    #col_drop_list = pri_data.filter(regex='TOKYO_ | CMA_ | HKO_ | KMA_ | NEWDEHLI_ | REUNION_ | BOM_ | NADI_ | WELLINGTON_ | DS824_ | TD9636_ | NEUMANN_').columns.tolist()

    hurr_redux = pd.DataFrame(hurr_data.drop(list(hurr_data.filter(regex = 'TOKYO_|CMA_|HKO_|KMA_|NEWDELHI_|REUNION_|BOM_|NADI_|WELLINGTON_|DS824_|TD9635_|NEUMANN_|WMO_|MLC_|TD9636_')), axis = 1, inplace = True ))

    # Drop first row from table which contains units
    hurr_redux = hurr_data.drop(index = 0)

    print(f"Data table columns reduced to {hurr_redux.shape[1]}")

    # Generate list of columns to convert to numeric data type 
    # Field names / wild match to update data type
    to_num = ['DIST2LAND','LANDFALL','WIND','PRES','SSHS','R34','R50','R64','ROCI','POCI','RMW','EYE','SEA','SPEED','DIR','LAT','LON','NUMBER']
    # Generate wildmatch list for regex use
    num_pat = '|'.join(to_num)

    # Numeric conversions

    # Convert date time from string to date time format
    hurr_redux['ISO_TIME'] = pd.to_datetime(hurr_redux['ISO_TIME'])

    # Convert other fields that should be numerical to numeric format from string
    # list of columns to be reformatted to numeric
    num_list = hurr_redux.filter(regex = num_pat).columns

    # update column content format and replace blanks/text with NaN
    for col in num_list:
        hurr_redux[col] = pd.to_numeric(hurr_redux[col], errors = 'coerce')

    # Set a date field
    hurr_redux['DATE'] = hurr_redux['ISO_TIME'].dt.date

    # Generate a list of hurricanes

    # Pull subset of columns to describe storms
    hurr_list = hurr_redux[['SID','SEASON','NAME','NATURE','USA_SSHS']]
    # Remove duplicates
    hurr_list = hurr_list.drop_duplicates()

    #hurr_list.head()

    # Summary list of hurricanes with maximum storm category observed
    hurr_sum_list = hurr_list[['SID','SEASON','NAME','USA_SSHS']]
    hurr_sum_list = hurr_list[['SID','SEASON','NAME','USA_SSHS']].groupby(['SID','SEASON','NAME'])['USA_SSHS'].max().reset_index()

    hurr_sum_list.rename(columns = {'USA_SSHS': 'MAX CAT'}, inplace=True)

    # Summary list of hurricanes with start and end dates and duration
    # Pull subset of columns to describe storms
    hurr_work = hurr_redux[['SID', 'ISO_TIME']]
    # Remove duplicates
    hurr_work = hurr_work.drop_duplicates()

    # Storm Start Date
    hurr_work_min = hurr_work[['SID', 'ISO_TIME']].groupby(['SID'])['ISO_TIME'].min().reset_index()
    hurr_work_min.rename(columns={'ISO_TIME': 'START DATE'}, inplace=True)

    # Storm End Date
    hurr_work_max = hurr_work[['SID', 'ISO_TIME']].groupby(['SID'])['ISO_TIME'].max().reset_index()
    hurr_work_max.rename(columns={'ISO_TIME': 'END DATE'}, inplace=True)

    # Storm Duration
    hurr_dur = pd.merge(hurr_work_min, hurr_work_max, on='SID', how='left')

    hurr_dur['STORM DURATION'] = (hurr_dur['END DATE'] - hurr_dur['START DATE']).dt.days

    hurr_sum_list = pd.merge(hurr_sum_list,hurr_dur, on='SID', how='left')
    hurr_sum_list.head()

    # Create data frames with only storms from 2022-2025 to align with gas data availability
    # Maintain data frames with all data for reference

    hurr_redux_rec = hurr_redux[(hurr_redux['SEASON'] >2021)]
    hurr_list_rec = hurr_list[(hurr_list['SEASON'] > 2021)]
    hurr_sum_list_rec = hurr_sum_list[(hurr_sum_list['SEASON'] > 2021)]

    # Create data frame of hurricanes from 2022-2025
    hurr_list_hurr_rec = hurr_sum_list[(hurr_sum_list['MAX CAT']>0) & (hurr_sum_list['SEASON']>2021)]
    hurr_redux_rec_hur = pd.merge(hurr_list_hurr_rec,hurr_redux_rec,on = 'SID', how = 'left')

    print('Hurricane data cleaning complete')

    return hurr_redux, hurr_list, hurr_sum_list, hurr_redux_rec, hurr_list_rec, hurr_sum_list_rec, hurr_redux_rec_hur


def gas_clean(gas_data):
    print(f'Cleaning {gas_data.name}')
    
    import numpy as np
    import pandas as pd
    from datetime import datetime, date, timedelta 

    # Filter to include only current average gas prices
    #gas_data_redux = gas_data[(gas_data['label'] == 'Current Avg.')]
    gas_data_redux = gas_data

    # Drop column wayback_timestamp (time stamp for data collection)
    gas_data_redux = gas_data_redux.drop(columns = 'wayback_timestamp')

    # Convert lat & lon values to numeric
    #gas_data_redux['lat'] = pd.to_numeric(gas_data_redux['lat'])
    #gas_data_redux['lng'] = pd.to_numeric(gas_data_redux['lng'])

    # Round gas prices to three places
    gas_data_redux[['regular','mid','premium','diesel']] = gas_data_redux[['regular','mid','premium','diesel']].round(3)

    # Convert date string to datetime format
    gas_data_redux['date'] = pd.to_datetime(gas_data_redux['date'])

    # Drop duplicates
    gas_data_redux = gas_data_redux.drop_duplicates()

    # Sort data by metro area and date
    gas_data_redux = gas_data_redux.sort_values(['metro','date'])

    # Change date of "yesterday avg." and "week ago avg." to their "current dates"
    mask = gas_data_redux['label'] == 'Yesterday Avg.'
    gas_data_redux.loc[mask, 'date'] = gas_data_redux.loc[mask, 'date'] - timedelta(days=1)

    mask2 = gas_data_redux['label'] == 'Week Ago Avg.'
    gas_data_redux.loc[mask2, 'date'] = gas_data_redux.loc[mask2, 'date'] - timedelta(days=7)

    # Drop month ago and year ago data
    mask3 = (gas_data_redux['label'] == 'Month Ago Avg.') | (gas_data_redux['label'] == 'Year Ago Avg.')
    gas_data_redux = gas_data_redux.loc[~mask3]

    # Drop label column
    gas_data_redux = gas_data_redux.drop(columns = ['label'])

    # Interpolate to set a gas price for each day
    gas_data_redux  = (gas_data_redux
                .set_index('date')
                .groupby('metro')
                .resample('D')
                .mean()
                .interpolate('linear')
                .reset_index())

    # Create year and month features for binning
    gas_data_redux['year'] = gas_data_redux['date'].dt.year
    gas_data_redux['month'] = gas_data_redux['date'].dt.month
    
    # Create date and datetime keys
    gas_data_redux['date_key'] = gas_data_redux['date']

    gas_data_redux['date_time_key'] = gas_data_redux['date'] + timedelta(hours = 12, minutes = 0, seconds = 0)

    print('Gas data cleaning complete')
    return gas_data_redux
