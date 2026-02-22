# clean.py

# hurr_data_clean

# hurricane data file is hurr_data

def hurr_clean(hurr_data):
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

    # Create data frames with only storms from 2022-2025 to align with gas data availability
    # Maintain data frames with all data for reference

    hurr_redux_rec = hurr_redux[(hurr_redux['SEASON'] >2021)]
    hurr_list_rec = hurr_list[(hurr_list['SEASON'] > 2021)]
    hurr_sum_list_rec = hurr_sum_list[(hurr_sum_list['SEASON'] > 2021)]

    print('Hurricane data cleaning complete')

    return hurr_redux, hurr_list, hurr_sum_list, hurr_redux_rec, hurr_list_rec, hurr_sum_list_rec


def gas_clean(gas_data):
    import numpy as np
    import pandas as pd
    from datetime import datetime, date, timedelta 

    # Filter to include only current average gas prices
    #gas_data_redux = gas_data[(gas_data['label'] == 'Current Avg.')]
    gas_data_redux = gas_data

    # Convert lat & lon values to numeric
    gas_data_redux['lat'] = pd.to_numeric(gas_data_redux['lat'])
    gas_data_redux['lng'] = pd.to_numeric(gas_data_redux['lng'])

    # Convert date string to datetime format
    gas_data_redux['date'] = pd.to_datetime(gas_data_redux['date'])

    # Create date and datetime keys
    gas_data_redux['date_key'] = gas_data_redux['date']

    gas_data_redux['date_time_key'] = gas_data_redux['date'] + timedelta(hours = 12, minutes = 0, seconds = 0)

    print('Gas data cleaning complete')
    return gas_data_redux