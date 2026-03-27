# model data prep1

# import libraries 
import pandas as pd
import numpy as np
#pip install geopy
from geopy import distance
import math
from datetime import datetime, date, timedelta, time

# additional cleaning for hurrican data

# import hurr_data_redux_rec_hur

def hurr_data_prep(hurr_data):
        
    # additional columns that are duplicative or not being evaluated for modeling
    col_to_remove1 = ['SEASON_y','NUMBER','BASIN','SUBBASIN','NAME_y','LAT','LON','TRACK_TYPE','IFLAG','USA_AGENCY','USA_ATCF_ID']
    col_to_remove2 = ['USA_R34_NE','USA_R34_SE','USA_R34_SW','USA_R34_NW','USA_R50_NE','USA_R50_SE','USA_R50_SW','USA_R50_NW',
                     'USA_R64_NE','USA_R64_SE','USA_R64_SW','USA_R64_NW','USA_SEARAD_NE','USA_SEARAD_SE','USA_SEARAD_SW','USA_SEARAD_NW']

    # remove columns in place
    hurr_mod_data = hurr_data.drop(col_to_remove1, axis = 1)
    hurr_mod_data.drop(col_to_remove2, axis = 1, inplace = True)
    
    # fix/rename columns
    hurr_mod_data.rename(columns={'SEASON_x': 'SEASON', 'NAME_x': 'NAME'}, inplace=True)
    #hurr_mod_data.columns

    # configure date columns
    hurr_mod_data['START DATE'] = hurr_mod_data['START DATE'].dt.date
    hurr_mod_data['END DATE'] = hurr_mod_data['END DATE'].dt.date

    return hurr_mod_data


def mod_data_config(hurr_mod_data, gas_data, metro_loc_data):
    from datetime import datetime, timedelta, date, time

    # select columns for configuring modeling parmeters
    dt_sel_data = hurr_mod_data[['SID','SEASON','NAME','START DATE','END DATE','ISO_TIME','DIST2LAND', 'LANDFALL','USA_LAT','USA_LON','USA_WIND','USA_SSHS','STORM_SPEED','STORM_DIR','DATE']]

    # list of storms in data set
    storm_list_ = dt_sel_data['NAME'].unique()
    storm_list = pd.DataFrame(storm_list_)
    storm_list.columns = ['NAME']

    # pare dataset down to one hurricane status line per day - default is 12:00 report
    # if 12:00 report not available, use earliest report available

    dlist = []
    list_of_dfs = []
    c = 0
    
    s = len(storm_list)
    
    # step through each storm entry 
    for n in range(s):
        storm = storm_list['NAME'].iat[n]
    
        extract = []

        # extract data for selected storm
        h_data = dt_sel_data[dt_sel_data['NAME'] == storm]
        h_data.reset_index(drop = True, inplace = True)

        # number of observations for storm
        L = len(h_data)
        #print(f'h_data is {L}')

        # list of dates of storm observations
        D =h_data['DATE'].unique()
        #print(D)
        Dates =  pd.DataFrame(D)
        Dates.columns = ['DATE']
        
        Dates['DATE1'] = pd.to_datetime(Dates['DATE'])
        #Dates['DATE1'] = Dates['DATE'].dt.date
        #print(Dates)

        # number of days of sotrm
        k = len(Dates)
        #print(f'Dates is {k}')
    
        if c == 0:
           ex_set = []

        # step through days of storm observations
        # target observation time is 12:00
        timechk = time(12,0,0)
        
        for i in range(k):
            datechk = Dates['DATE'].iat[i]
        
            fil = []

            # filter observations for selected day
            fil = h_data[h_data['DATE'] == datechk]
            fil.reset_index(drop = True, inplace = True)
            
            # find row where 12:00 observation is reported
            find_row = fil[fil['ISO_TIME'].dt.time == timechk]
        
            matchrow = find_row.index.tolist()

            # if no 12:00 observation exists, take the first observation
            if not matchrow:
               matchrow.append(0)
        
           # print(matchrow)
        
            ext = matchrow[0]
            #print(ext)
        
            ex_row = fil.loc[ext]
            #print(ex_row)
        
            ex_set.append(ex_row)

        # generate list of row numbers to extract for one observation for each day
        extract = pd.DataFrame(ex_set)
        list_of_dfs.append(extract)
        #print(extract)
    
        c = c + 1
    DL = pd.concat(list_of_dfs, ignore_index=True)

    # prompt user to select metro area of interest
    #metro_all =  metro_loc_data['metro'].unique().tolist()
    metro_all = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral', 'Miami','West Palm Beach-Boca Raton','Melbourne-Titusville','Daytona Beach','Jacksonville']

    print(metro_all)
    metro_sel = input('Enter metro area: ')
    print(f'{metro_sel} selected')

    # 
    # Metro Coordinates
    metro_ext = metro_loc_data[metro_loc_data['metro'] == metro_sel]
    metro_lat = metro_ext['lat'].item()
    metro_lon = metro_ext['lng'].item()
    
    metro_coord = (metro_lat, metro_lon)
    #print(metro_sel)
    #print(metro_coord)

    # down select data parameters
    storm_dt0 = extract[['SID', 'SEASON', 'NAME', 'DATE', 'START DATE', 'DIST2LAND', 'LANDFALL', 'USA_SSHS', 'STORM_SPEED', 'STORM_DIR']]
    storm_dt0['date_start'] = pd.to_datetime(storm_dt0['START DATE'])
    storm_dt0['date_key'] = pd.to_datetime(storm_dt0['DATE'])
    storm_dt0.reset_index(drop = True, inplace = True)
    #storm_dt0.head()

    L = len(extract)
    #print(L)
    
    dist2metro = []
    bear2metro = []
    bear2oil = []
    stormloc = []
    stormloc_bin = []
    inboundchk = []
    bear2oil = []
    oildist = []
    oilthreatdir = []
    storm_dur = []
    
    d2metro_cat = []
    d2oil_cat = []

    d2land_cat = []
    d2landfall_cat = []
    
    
    for i in range(L):
        # calculate duration of storm
        duration = (storm_dt0['date_key'].iat[i] - storm_dt0['date_start'].iat[i]).days
        storm_dur.append(duration)

        # storm position
        storm_lat = extract['USA_LAT'].iat[i].item()
        storm_lon = extract['USA_LON'].iat[i].item()
    
        storm_coord = (storm_lat, storm_lon)
    
        # distance from storm to metro
        dist = round((distance.distance(storm_coord, metro_coord).km))

        # categorize distance from storm to metro
        if dist <= 250:
            dist_cat  = 1
        elif dist > 250 & dist <= 500:
            dist_cat = 2
        elif dist > 500 & dist <= 1000:
            dist_cat = 3
        else:
            dist_cat = 4
    
        dist2metro.append(dist)
    
        d2metro_cat.append(dist_cat)
    
        
        # bearing from storm to metro
        
        # convert lat/lon position to radians
        # storm position
        lat1 = math.radians(storm_lat)
        lon1 = math.radians(storm_lon)
    
        # metro location
        lat2 = math.radians(metro_lat)
        lon2 = math.radians(metro_lon)
        
        delta_lon = lon2 - lon1

        # calculate bearing components
        y = math.sin(delta_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)

        # calculate bearing
        init_bearing_rad = math.atan2(y,x)
        
        # convert to degrees
        init_bearing_deg = math.degrees(init_bearing_rad)
        
        # normalize to compass bearing
        bearing_to_metro = round((init_bearing_deg + 360) % 360)
    
        bear2metro.append(bearing_to_metro)

        # storm direction observation
        storm_dir = extract['STORM_DIR'].iat[i]
            
        # determine storm position (ATL or GULF)
        # if north of Daytona Beach lat, use lon of Jacksonville otherwise use lon of Daytona Beach
        # as the dividing line to determine which side of FL storm is on
        # Daytona Beach lat 
        loc_chk_lat = 29.174
        # Jacksonville lon
        loc_chk_lon1 = -81.7923
        # Daytona Beach lon
        loc_chk_lon2 = -81.2197
        
        if storm_lat >= loc_chk_lat:
            if storm_lon >= loc_chk_lon1:
                storm_pos = 'ATL'
                storm_pos_bin = 1
            else:
                storm_pos = 'GULF'
                storm_pos_bin = 0
        else:
            if storm_lon >= loc_chk_lon2:
                storm_pos = 'ATL'
                storm_pos_bin = 1
            else:
                storm_pos = 'GULF'
                storm_pos_bin = 0
        
        stormloc.append(storm_pos)
        stormloc_bin.append(storm_pos_bin)
    
        # Storm travel towards metro?
    
        if abs(bearing_to_metro - storm_dir) <= 45:
            inbound = True
        else:
            inbound = False
        
        inboundchk.append(inbound)
        
        # storm threat to oil rigs?
    
        oil_lat = 28.098
        oil_lon = -92.549
        
        oil_coord = (oil_lat, oil_lon)
        
        oil_dist = round((distance.distance(storm_coord, oil_coord).km))
        #print(oil_dist)
    
        if oil_dist <= 250:
            oil_dist_cat  = 1
        elif oil_dist > 250 & oil_dist <= 500:
            oil_dist_cat = 2
        elif oil_dist > 500 & oil_dist <= 1000:
            oil_dist_cat = 3
        else:
            oil_dist_cat = 4
    
        d2oil_cat.append(oil_dist_cat)
        
        oildist.append(oil_dist)
        
        lat3 = math.radians(oil_lat)
        lon3 = math.radians(oil_lon)
        
        delta_lon1 = lon3 - lon1
        
        y1 = math.sin(delta_lon1) * math.cos(lat3)
        x1 = math.cos(lat1) * math.sin(lat3) - math.sin(lat1) * math.cos(lat3) * math.cos(delta_lon1)
        
        init_bearing_rad1 = math.atan2(y1,x1)
        
        # convert to degrees
        init_bearing_deg1 = math.degrees(init_bearing_rad1)
        
        # normalize to compass bearing
        
        bearing_to_oil = round((init_bearing_deg1 + 360) % 360)
        #print(bearing_to_oil)
        bear2oil.append(bearing_to_oil)
        
        
        if storm_pos == 'GULF':
            if abs(bearing_to_oil - storm_dir) <= 45:
                oil_threat_dir = True
            else:
                oil_threat_dir = False
            
        else:
            oil_threat_dir = False
        
        #print(oil_threat_dir)
        oilthreatdir.append(oil_threat_dir)

        # category for distance to land
        d2l = storm_dt0['DIST2LAND'].iat[i].item()
    
        if d2l <= 250:
            d2l_cat  = 1
        elif d2l > 250 & d2l <= 500:
            d2l_cat= 2
        elif d2l > 500 & d2l <= 1000:
            d2l_cat = 3
        else:
            d2l_cat = 4
    
        d2land_cat.append(d2l_cat)

        # category for distance to landfall
        d2lf = storm_dt0['LANDFALL'].iat[i].item()
    
        if d2lf <= 250.0:
            d2lf_cat  = 1
        elif (d2lf > 250.0) & (d2lf <= 500.0):
            d2lf_cat= 2
        elif (d2lf > 5.000) & (d2lf <= 1000.0):
            d2lf_cat = 3
        else:
            d2lf_cat = 4
    
        d2landfall_cat.append(d2lf_cat)

    # add parameters to data frame
    storm_dt0['DIST2METRO'] = dist2metro
    storm_dt0['BEAR2METRO'] = bear2metro 
    #storm_dt0['BEAR2OIL'] = bear2oil
    storm_dt0['STORM_LOC'] = stormloc
    storm_dt0['STORM_LOC_BIN'] = stormloc_bin
    storm_dt0['INBOUND'] = inboundchk
    storm_dt0['DIST2OIL'] = oildist
    storm_dt0['OIL_THT'] = oilthreatdir
    storm_dt0['STORM_LEN'] = storm_dur
    storm_dt0['CD2LAND'] = d2land_cat
    storm_dt0['CD2LANDFALL'] = d2landfall_cat
    storm_dt0['CD2METRO'] = d2metro_cat
    storm_dt0['CD2OIL'] = d2oil_cat

    # gas data

    # filter gas data on selected metro area
    h2_gas = gas_data[(gas_data['metro'] == metro_sel)]

    # 30 day average price
    h2_gas['30d_avg_reg'] = h2_gas['regular'].rolling(window = 30, min_periods = 1).mean().shift(1).round(3)
    h2_gas['30d_avg_mid'] = h2_gas['mid'].rolling(window = 30, min_periods = 1).mean().shift(1).round(3)
    h2_gas['30d_avg_pre'] = h2_gas['premium'].rolling(window = 30, min_periods = 1).mean().shift(1).round(3)
    
    # daily change in price 
    h2_gas['daily_del_reg'] = h2_gas['regular'].diff().round(3)
    h2_gas['daily_del_mid'] = h2_gas['mid'].diff().round(3)
    h2_gas['daily_del_pre'] = h2_gas['premium'].diff().round(3)
    
    # percentage daily change
    h2_gas['daily_pctd_reg'] = h2_gas['regular'].pct_change().round(3)
    h2_gas['daily_pctd_mid'] = h2_gas['mid'].pct_change().round(3)
    h2_gas['daily_pctd_pre'] = h2_gas['premium'].pct_change().round(3)

    # compile storm and gas data
    storm_dt2 = pd.merge(storm_dt0, h2_gas[['metro', 'date_key', 'regular',	'mid', 'premium', 'month', '30d_avg_reg', '30d_avg_mid', '30d_avg_pre', 'daily_del_reg', 'daily_del_mid', 
                                            'daily_del_pre', 'daily_pctd_reg', 'daily_pctd_mid', 'daily_pctd_pre']], on = 'date_key', how = 'left')


    # find 30 day average gas prices for start of each storm
    
    storm_30av_r = []
    storm_30av_m = []
    storm_30av_p = []
    
    for k in range(len(storm_dt2)):
        #print(storm_dt2['NAME'].iat[k])
        #print(storm_dt2['STORM_LEN'].iat[k])
        
        # Is row start of storm?
        if storm_dt2['STORM_LEN'].iat[k] == 0:           
            # set row for start of storm
            sel = k

            # set 30 day avg value for storm
            s_av_reg = storm_dt2['30d_avg_reg'].iat[k]
            s_av_mid = storm_dt2['30d_avg_mid'].iat[k]
            s_av_pre = storm_dt2['30d_avg_pre'].iat[k]
    
        else:
            # set 30 day avg value based on start of storm
            s_av_reg = storm_dt2['30d_avg_reg'].iat[sel]
            s_av_mid = storm_dt2['30d_avg_mid'].iat[sel]
            s_av_pre = storm_dt2['30d_avg_pre'].iat[sel]
    
        storm_30av_r.append(s_av_reg)
        storm_30av_m.append(s_av_mid)
        storm_30av_p.append(s_av_pre)
    
    # add to data frame
    storm_dt2['storm_30d_avg_reg'] = storm_30av_r
    storm_dt2['storm_30d_avg_mid'] = storm_30av_m
    storm_dt2['storm_30d_avg_pre'] = storm_30av_p

    # calculate precent change from 30 day average prices
    storm_dt2['storm_pct_avg_reg'] = ((storm_dt2['regular'] - storm_dt2['storm_30d_avg_reg'])/storm_dt2['storm_30d_avg_reg']).round(3)
    storm_dt2['storm_pct_avg_mid'] = ((storm_dt2['mid'] - storm_dt2['storm_30d_avg_mid'])/storm_dt2['storm_30d_avg_mid']).round(3)
    storm_dt2['storm_pct_avg_pre'] = ((storm_dt2['premium'] - storm_dt2['storm_30d_avg_pre'])/storm_dt2['storm_30d_avg_pre']).round(3)

    # set buy decisions - for avg % change and for daily % change
    buyavg = []
    buyday = []
    
    for z in range(len(storm_dt2)):
        if storm_dt2['storm_pct_avg_reg'].iat[z] > 0.02:
            buyavg_ = True
        else:
            buyavg_ = False
    
        if storm_dt2['daily_pctd_reg'].iat[z] > 0.02:
            buyday_ = True
        else:
            buyday_ = False
    
        buyavg.append(buyavg_)
        buyday.append(buyday_)
    
    storm_dt2['buy_avg'] = buyavg
    storm_dt2['buy_day'] = buyday

    model_data = storm_dt2[['SID','SEASON','NAME','date_key','DIST2LAND','CD2LAND','LANDFALL','CD2LANDFALL','USA_SSHS','metro',
                            'DIST2METRO','CD2METRO','STORM_LOC','INBOUND','DIST2OIL','CD2OIL','OIL_THT','STORM_LEN','buy_avg','buy_day']]

    return storm_dt2, model_data

    