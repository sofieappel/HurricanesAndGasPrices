# stats_look.py

# Run basic statistical analysis and plots for data sets

def sum_stats(dataset):
    print(f'Statistics for {dataset.name}')

    # Overview of data set
    info_sum = dataset.info
    print(info_sum)

    # Check for null values
    null_sum = dataset.isnull().sum().sort_values(ascending = False)
    print(null_sum)

    # Stats summary for data set
    stat_sum = dataset.describe()
    print(stat_sum)

def stats_hurr_viz(hd):
    # Install necessary libraries
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    # Show distribution of Storm Speed
    plt.figure(figsize=(20, 5))
    sns.histplot(data=hd, x='STORM_SPEED')
    plt.title(f'Storm Speed Distribution')
    plt.xlabel('Storm Speed (kts)')
    plt.ylabel('Count')
    plt.show()

    # Show distribution of Storm Speed by Storm Category
    plt.figure(figsize=(20, 5))
    sns.stripplot(data = hd, x = 'USA_SSHS', y = 'STORM_SPEED')
    plt.title(f'Storm Speed by Storm Category')
    plt.xlabel('Storm Category (SSHS)')
    plt.ylabel('Storm Speed (kts)')
    plt.show()

    # Show distribution of Landfall
    plt.figure(figsize=(20, 5))
    sns.histplot(data=hd, x='LANDFALL')
    plt.title(f'Landfall Distance Distribution')
    plt.xlabel('Nearest location to land within next timestep (km)')
    plt.ylabel('Count')
    plt.show()

    # Show distribution of Distance to Land
    plt.figure(figsize=(20, 5))
    sns.histplot(data=hd, x='DIST2LAND')
    plt.title(f'Distance to Land Distribution')
    plt.xlabel('Distance to Land (km)')
    plt.ylabel('Count')
    plt.show()

    # Show scatter plot of Distance to Land & Landfall
    plt.figure(figsize=(20, 5))
    sns.pointplot(data=hd, x='DIST2LAND', y = 'LANDFALL')
    plt.title(f'Distance to Land vs Landfall')
    plt.xlabel('Distance to Land (km)')
    plt.ylabel('Landfall - Nearest location to land in next timestep (km)')
    plt.show()

    # Show distribution of Wind Speed
    plt.figure(figsize=(20, 5))
    sns.histplot(data=hd, x='USA_WIND')
    plt.title(f'Storm Wind Speed Distribution')
    plt.xlabel('Wind Speed (kts)')
    plt.ylabel('Count')
    plt.show()

    # Show distribution of Storm Category
    plt.figure(figsize=(20, 5))
    sns.histplot(data=hd, x='USA_SSHS')
    plt.title(f'Storm Category (SSHS) Distribution')
    plt.xlabel('Storm Category (SSHS)')
    plt.ylabel('Count')
    plt.show()

#def stats_gas_viz():
