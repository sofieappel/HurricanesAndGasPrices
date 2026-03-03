# eda_visuals.py

def hurr_visuals(hurr_sum_list):
    print(f'Starting EDA for {hurr_sum_list.name}')
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    min_year = min(hurr_sum_list['SEASON'])
    max_year = max(hurr_sum_list['SEASON'])
    if min_year < 2000:
        filt_year = 2000
    else:
        filt_year = min_year


        # Count of Tropical Storms by Season (year)
    plt.figure(figsize=(20, 5))
    sns.countplot(data=hurr_sum_list, x='SEASON')
    plt.title(f'Tropical Storms ({min_year}-{max_year})')
    plt.xlabel('Season (Year)')
    plt.ylabel('Count of Storms')
    plt.show()

    # Count of Tropial Storms 2000 - 2025
    plt.figure(figsize=(20, 5))
    sns.countplot(data=hurr_sum_list[(hurr_sum_list['SEASON'] >= filt_year)], x='SEASON')
    plt.title(f'Tropical Storms ({filt_year}-{max_year})')
    plt.xlabel('Season (Year)')
    plt.ylabel('Count of Storms')
    plt.show()

    # Count of Hurricanes 2000-2025
    plt.figure(figsize=(20, 5))
    sns.countplot(data=hurr_sum_list[(hurr_sum_list['SEASON'] >= filt_year) & (hurr_sum_list['MAX CAT'] >= 1)], x='SEASON')
    plt.title(f'Hurricanes ({filt_year}-{max_year})')
    plt.xlabel('Season (Year)')
    plt.ylabel('Count of Storms')
    plt.show()

    # Hurricanes by Season & Category 2000-2025
    plt.figure(figsize=(20, 5))
    sns.swarmplot(data=hurr_sum_list[(hurr_sum_list['SEASON'] >= filt_year) & (hurr_sum_list['MAX CAT'] >= 1)], x='SEASON',
                  y='MAX CAT', hue='MAX CAT', dodge=True, palette='crest')
    plt.title(f'Hurricanes ({filt_year}-{max_year})')
    plt.xlabel('Season (Year)')
    plt.ylabel('Count of Storms')
    plt.show()

def gas_visuals_ov(gas_data, metro_grp):
    print(f'Starting overview for {gas_data.name} and {metro_grp}')
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    gas_data_redux = gas_data[(gas_data['metro'].isin(metro_grp))]

    min_year = min(gas_data_redux['year'])
    max_year = max(gas_data_redux['year'])

    # Time Hist of gas prices by locality
    plt.figure(figsize=(20, 10))
    sns.lineplot(data=gas_data_redux, x='date', y='regular', hue='metro')
    # plt.axvspan(datetime.date(2025, 6, 1), datetime.date(2025, 11, 30), alpha = 0.3)
    plt.title(f'Regular Gas Price ({min_year}-{max_year})')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

    # Distribution of gas prices in reporting period
    #plt.figure(figsize=(20, 10))
    sns.histplot(data=gas_data_redux, x='regular')
    plt.title(f'Regular Gas Price Distribution ({min_year}-{max_year})')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

    # Distribution of gas prices by locality
    #plt.figure(figsize=(20, 10))
    sns.displot(data=gas_data_redux, x='regular', hue='metro')
    plt.suptitle(f'Regular Gas Price Distribution by Metro Area ({min_year}-{max_year})')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

def gas_visuals(gas_data, metro_grp):
    print(f'Starting EDA for {gas_data.name} and {metro_grp}')
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    gas_data_redux = gas_data[(gas_data['metro'].isin(metro_grp))]

    min_year = min(gas_data_redux['year'])
    max_year = max(gas_data_redux['year'])

    # Histograms of gas prices by locality
    #plt.figure(figsize=(20, 10))
    sns.displot(data=gas_data_redux, x='regular', col='metro', col_wrap=3)
    plt.suptitle(f'Regular Gas Price Distribution ({min_year}-{max_year})', y = 0.99)
    plt.subplots_adjust(top=0.9)
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

    # Histograms of gas prices by locality and year
    #plt.figure(figsize=(20, 10))
    sns.displot(data=gas_data_redux, x='regular', col='metro', hue='year', col_wrap=3)
    plt.suptitle(f'Regular Gas Price Distribution by Year ({min_year}-{max_year})', y=0.99)
    plt.subplots_adjust(top=0.9)
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

    # Time Hist of gas prices by locality
    #plt.figure(figsize=(20, 5))
    sns.displot(data=gas_data_redux, x='regular', hue='metro')
    plt.suptitle(f'Regular Gas Price ({min_year}-{max_year})')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

    # Box plot of regular gas prices overall
    sns.boxplot(data=gas_data_redux, x='regular')
    plt.title(f'Distribution of Regular Gas Price ({min_year}-{max_year})')
    plt.xlabel('Gas Price (Regular)')
    plt.show()

    # Box plot of regular gas prices by year
    sns.catplot(data=gas_data_redux, x='regular', dodge=True,
                kind='box', col='year')
    plt.title(f'Distribution of Regular Gas Price by Year ({min_year}-{max_year})')
    plt.xlabel('Gas Price (Regular)')
    plt.show()

    # Box plot of regular gas prices by metro
    sns.boxplot(data=gas_data_redux, x='regular', y='metro')
    plt.title(f'Distribution of Regular Gas Price by Metro ({min_year}-{max_year})')
    plt.xlabel('Gas Price (Regular)')
    plt.show()

    # Box plot of regular gas prices by metro & year
    sns.catplot(data=gas_data_redux, x='regular', y='metro', hue='metro', dodge=True,
                kind='box', col='year')
    plt.title(f'Distribution of Regular Gas Price by Metro & Year ({min_year}-{max_year})')
    plt.xlabel('Gas Price (Regular)')
    plt.show()

