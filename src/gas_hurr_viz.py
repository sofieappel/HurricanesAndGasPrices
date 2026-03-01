#gas_hurr_viz.py

def gas_timehist(hurr_data, gas_data, metro):
    # create list of hurricane seasons
    season_x = pd.DataFrame(hurr_data['SEASON'].unique(), columns=['season'])

    s = season_x.shape[0]
    start = [] * s
    end = [] * s
    #print(start)

    for i in range(s):
        y = season_x['season'][i]
        print(y)
        sdt = date(y, 6, 1)
        edt = date(y, 11, 30)
        start.append(sdt)
        end.append(edt)
        # season_x['start'] = date(year,6,1)
    season_x['start'] = start
    season_x['end'] = end
    #print(season_x)

    # Plot gas prices and hurricane season
    plt.figure(figsize=(20, 10))
    sns.lineplot(data=gas_data_redux, x='date', y='regular', hue='metro')
    plt.title(f'Regular Gas Price')
    plt.xlabel('Date')
    plt.ylabel('Gas Price (Regular)')
    s = season_x.shape[0]

    for i in range(s):
        print(i)
        plt.axvspan(season_x['start'][i], season_x['end'][i],
                    alpha=0.3)  # label='Highlighted Region' if interval_start == highlight_intervals[0][0] else ""

    plt.show()
