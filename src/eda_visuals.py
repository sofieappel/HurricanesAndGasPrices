# eda_visuals.py

def hurr_visuals(hurr_sum_list):
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

def gas_visuals(gas_data_redux):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    # Histograms of gas prices by locality
    plt.figure(figsize=(20, 5))
    sns.displot(data=gas_data_redux, x='regular', col='metro', col_wrap=4)
    plt.title(f'Regular Gas Price')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()

    # Time Hist of gas prices by locality
    plt.figure(figsize=(20, 5))
    sns.lineplot(data=gas_data_redux, x='date', y='regular', hue='metro')
    plt.title(f'Regular Gas Price')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    plt.show()