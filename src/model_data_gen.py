# model_data_gen.py

def model_dataset(hurr_mod_data, gas_data_redux, metro_loc_data):
    # import libraries 
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # import for distance calculations
    #pip install geopy
    from geopy import distance
    import math
    
    # import datetime 
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
    
        # number of days of strrm
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

    # down select data parameters
    storm_dt0 = extract[['SID', 'SEASON', 'NAME', 'DATE', 'START DATE', 'DIST2LAND', 'LANDFALL', 'USA_SSHS', 'STORM_SPEED', 'STORM_DIR']]
    storm_dt0['date_start'] = pd.to_datetime(storm_dt0['START DATE'])
    storm_dt0['date_key'] = pd.to_datetime(storm_dt0['DATE'])
    storm_dt0.reset_index(drop = True, inplace = True)
    #storm_dt0.head()
    
    L = len(extract)
    #print(L)
    storm_cat = []
    
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
    
    metro_name = []
    
    date_obs = []
    
    gas_col = []
    
    # prompt user to select metro area of interest
    #metro_all =  metro_loc_data['metro'].unique().tolist()
    metro_all = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral', 'Miami','West Palm Beach-Boca Raton','Melbourne-Titusville','Daytona Beach','Jacksonville']
    
    #print(metro_all)
    #metro_sel = input('Enter metro area: ')
    #metro_sel = metro

    for metro_sel in metro_all:
        print(f'{metro_sel} selected')
    
        gasf = []
    
        # Metro Coordinates
        metro_ext = metro_loc_data[metro_loc_data['metro'] == metro_sel]
        metro_lat = metro_ext['lat'].item()
        metro_lon = metro_ext['lng'].item()
        
        metro_coord = (metro_lat, metro_lon)
        #print(metro_sel)
        #print(metro_coord)
    
        gasf = gas_data_redux[(gas_data_redux['metro'] == metro_sel)]
        #print(gasf[0:5])
    
        # 30 day average price
        gasf['30d_avg_reg'] = gasf['regular'].rolling(window = 30, min_periods = 1).mean().shift(1).round(3)
        gasf['30d_avg_mid'] = gasf['mid'].rolling(window = 30, min_periods = 1).mean().shift(1).round(3)
        gasf['30d_avg_pre'] = gasf['premium'].rolling(window = 30, min_periods = 1).mean().shift(1).round(3)
        
        # daily change in price 
        gasf['daily_del_reg'] = gasf['regular'].diff().round(3)
        gasf['daily_del_mid'] = gasf['mid'].diff().round(3)
        gasf['daily_del_pre'] = gasf['premium'].diff().round(3)
        
        # percentage daily change
        gasf['daily_pctd_reg'] = gasf['regular'].pct_change().round(3)
        gasf['daily_pctd_mid'] = gasf['mid'].pct_change().round(3)
        gasf['daily_pctd_pre'] = gasf['premium'].pct_change().round(3)
    
        #print(gasf[0:5])
    
    
        for i in range(L):
            # selected metro
            metro_name.append(metro_sel)
    
            # date
            obs_date = storm_dt0['date_key'].iat[i]
            date_obs.append(obs_date) 
    
            # calculate duration of storm
            duration = (storm_dt0['date_key'].iat[i] - storm_dt0['date_start'].iat[i]).days
            storm_dur.append(duration)
    
            # storm category
            stormcat = storm_dt0['USA_SSHS'].iat[i]
            storm_cat.append(stormcat)
    
            # gas data
            gasday = gasf[gasf['date_key'] == obs_date]
            gas_col.append(gasday)
    
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
                inbound = 1
            else:
                inbound = 0
            
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
                    oil_threat_dir = 1
                else:
                    oil_threat_dir = 0
                
            else:
                oil_threat_dir = 0
            
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
    
        if metro_sel == 'Pensacola':
            gasfm = pd.DataFrame(gasf)
        else:
            gasfm = pd.concat([gasfm, gasf])


    gasfm.rename(columns = {"metro":"METRO"}, inplace = True)
    gasfm.head()

    storm_metro = pd.DataFrame(date_obs)
    storm_metro.columns = ['date_key']

    # add parameters to data frame
    storm_metro['METRO'] = metro_name
    storm_metro['USA_SSHS'] = storm_cat
    #storm_metro['date_key'] = date_obs
    storm_metro['DIST2METRO'] = dist2metro
    storm_metro['BEAR2METRO'] = bear2metro 
    #storm_dt0['BEAR2OIL'] = bear2oil
    storm_metro['STORM_LOC'] = stormloc
    storm_metro['STORM_LOC_BIN'] = stormloc_bin
    storm_metro['INBOUND'] = inboundchk
    storm_metro['DIST2OIL'] = oildist
    storm_metro['OIL_THT'] = oilthreatdir
    storm_metro['STORM_LEN'] = storm_dur
    storm_metro['CD2LAND'] = d2land_cat
    storm_metro['CD2LANDFALL'] = d2landfall_cat
    storm_metro['CD2METRO'] = d2metro_cat
    storm_metro['CD2OIL'] = d2oil_cat

    storm_dtx = pd.merge(storm_metro, gasfm[['METRO', 'date_key', 'regular', 'mid', 'premium', 'month', '30d_avg_reg', '30d_avg_mid', '30d_avg_pre', 'daily_del_reg', 'daily_del_mid', 
                                        'daily_del_pre', 'daily_pctd_reg', 'daily_pctd_mid', 'daily_pctd_pre']], on = ['METRO','date_key'], how = 'left')
    storm_dtx['md_key'] = storm_dtx['date_key'].astype(str) + '-' + storm_dtx['METRO'].astype(str)
    storm_dtx['month_no'] = storm_dtx['date_key'].dt.month

    # find 30 day average gas prices for start of each storm

    storm_30av_r = []
    storm_30av_m = []
    storm_30av_p = []
    
    for k in range(len(storm_dtx)):
        #print(storm_dt2['NAME'].iat[k])
        #print(storm_dt2['STORM_LEN'].iat[k])
        
        # Is row start of storm?
        if storm_dtx['STORM_LEN'].iat[k] == 0:           
            # set row for start of storm
            sel = k
    
            # set 30 day avg value for storm
            s_av_reg = storm_dtx['30d_avg_reg'].iat[k]
            s_av_mid = storm_dtx['30d_avg_mid'].iat[k]
            s_av_pre = storm_dtx['30d_avg_pre'].iat[k]
    
        else:
            # set 30 day avg value based on start of storm
            s_av_reg = storm_dtx['30d_avg_reg'].iat[sel]
            s_av_mid = storm_dtx['30d_avg_mid'].iat[sel]
            s_av_pre = storm_dtx['30d_avg_pre'].iat[sel]
    
        storm_30av_r.append(s_av_reg)
        storm_30av_m.append(s_av_mid)
        storm_30av_p.append(s_av_pre)
    
    # add to data frame
    storm_dtx['storm_30d_avg_reg'] = storm_30av_r
    storm_dtx['storm_30d_avg_mid'] = storm_30av_m
    storm_dtx['storm_30d_avg_pre'] = storm_30av_p
    
    # calculate precent change from 30 day average prices
    storm_dtx['storm_pct_avg_reg'] = ((storm_dtx['regular'] - storm_dtx['storm_30d_avg_reg'])/storm_dtx['storm_30d_avg_reg']).round(3)
    storm_dtx['storm_pct_avg_mid'] = ((storm_dtx['mid'] - storm_dtx['storm_30d_avg_mid'])/storm_dtx['storm_30d_avg_mid']).round(3)
    storm_dtx['storm_pct_avg_pre'] = ((storm_dtx['premium'] - storm_dtx['storm_30d_avg_pre'])/storm_dtx['storm_30d_avg_pre']).round(3)
    
    # set buy decisions - for avg % change and for daily % change
    buyavg = []
    buyday = []
    
    for z in range(len(storm_dtx)):
        if storm_dtx['storm_pct_avg_reg'].iat[z] > 0.02:
            buyavg_ = 1
        else:
            buyavg_ = 0
    
        if storm_dtx['daily_pctd_reg'].iat[z] > 0.02:
            buyday_ = 1
        else:
            buyday_ = 0
    
        buyavg.append(buyavg_)
        buyday.append(buyday_)
    
    storm_dtx['buy_avg'] = buyavg
    storm_dtx['buy_day'] = buyday
    
    # select model data
    model_data = storm_dtx[['md_key','USA_SSHS','STORM_LOC_BIN','CD2LAND','CD2LANDFALL','CD2METRO','INBOUND',
                        'CD2OIL','OIL_THT','STORM_LEN','month_no','buy_avg','buy_day']]

    return(storm_dtx, model_data)