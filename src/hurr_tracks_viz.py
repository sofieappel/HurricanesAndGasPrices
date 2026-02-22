# hurr_tracks_viz.py

def hurr_tracks_season(hurr_data_redux):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    # Grid Plot of Hurricane Tracks (2005)
    p1 = sns.relplot(data=hurr_data_redux[(hurr_data_redux['SEASON'] == 2005)], x='USA_LON', y='USA_LAT',
                     size='USA_SSHS', hue='USA_SSHS', col='NAME', col_wrap=3,
                     palette='crest')  # hue='day', style='time',

    p1.fig.suptitle("2009 Hurricane Season", fontsize=16, y=1.05)
    plt.show()


def hurr_tracks_single(hurr_data_redux, gc_data):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    plt.figure(figsize=(7, 7))
    sns.scatterplot(data=hurr_data_redux[(hurr_data_redux['SEASON'] == 2005) & (hurr_data_redux['NAME'] == 'KATRINA')], x='USA_LON',
                    y='USA_LAT', size='USA_SSHS', hue='USA_SSHS', palette='crest')
    # hue='day', style='time',, col='NAME', col_wrap = 3,size='USA_SSHS', hue = 'USA_SSHS',, palette = 'crest'
    plt.plot(gc_data['LON'], gc_data['LAT'], color='red', label='Data 2', linestyle='--')
    plt.title(f'Hurricane Katrina (2005)')
    # plt.xlabel('Season (Year)')
    # plt.ylabel('Count of Storms')
    plt.show()

def hurr_tracks_compare(hurr_data_redux, gc_data):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    plt.figure(figsize=(7, 7))
    sns.scatterplot(data=hurr_data_redux[(hurr_data_redux['SEASON'] == 2005) & (hurr_data_redux['NAME'] == 'RITA')], x='USA_LON',
                    y='USA_LAT', size='USA_SSHS', hue='USA_SSHS', palette='crest')
    sns.scatterplot(data=hurr_data_redux[(hurr_data_redux['SEASON'] == 2005) & (hurr_data_redux['NAME'] == 'KATRINA')], x='USA_LON',
                    y='USA_LAT', size='USA_SSHS', hue='USA_SSHS', palette='magma')
    # hue='day', style='time',, col='NAME', col_wrap = 3,size='USA_SSHS', hue = 'USA_SSHS',, palette = 'crest'
    plt.plot(gc_data['LON'], gc_data['LAT'], color='red', label='Data 2', linestyle='--')
    plt.title(f'Hurricane Rita (2005)')
    # plt.xlabel('Season (Year)')
    # plt.ylabel('Count of Storms')
    plt.show()