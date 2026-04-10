# modeling_fcns.py

def model_setup(model,y_param,testsplit = 0.2):
    from sklearn.model_selection import train_test_split
    
    X = model.drop(y_param, axis = 1)
    y = model[y_param]
    
    X_train, X_test, y_train, y_test =  train_test_split(X, y, test_size = testsplit, random_state = 42)

    features_list = X.columns.tolist()

    return(X_train, X_test, y_train, y_test, features_list)

def model_stats_analysis(y_test,y_pred,X_test,model):
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
     
    # compute performance on test set
    mse = mean_squared_error(y_test, y_pred)
    print("Mean Squared Error: ", mse)
    
    r2 = r2_score(y_test, y_pred)
    print("R-squared: ", r2)

    acc_sc = accuracy_score(y_test,y_pred)
    #print('accuracy score: %.2f' % acc_sc)

    prec_sc = precision_score(y_test,y_pred,zero_division=np.nan)
    #print('precision score: %.2f' % prec_sc)

    rec_sc = recall_score(y_test,y_pred)
    #print('recall score: %.2f' % rec_sc)

    f1_sc = f1_score(y_test,y_pred)
    #print('f1 score: %.2f' % f1_sc)

    class_rep = classification_report(y_test, y_pred, labels=None, target_names=None, sample_weight=None, digits=2, output_dict=False, zero_division=np.nan)
    print(class_rep)

    conf_mat = confusion_matrix(y_test, y_pred, labels=None, sample_weight=None, normalize=None)
    #print(conf_mat)

    # Create confusion matrix heatmap
    plt.figure(figsize=(4, 4))
    
    plt.imshow(conf_mat, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    
    classes = ['Do Not Buy', 'Buy']
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    
    # Add annotations
    thresh = conf_mat.max() / 2.
    for i in range(conf_mat.shape[0]):
        for j in range(conf_mat.shape[1]):
            plt.text(j, i, format(conf_mat[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if conf_mat[i, j] > thresh else "black")

    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.show()

    # calculate ROC curve
    y_scores = model.predict_proba(X_test)
    fpr, tpr, thresholds = roc_curve(y_test, y_scores[:,1])
    
    # plot ROC curve
    fig = plt.figure(figsize=(4, 4))
    # plot the diagonal 50% line
    plt.plot([0, 1], [0, 1], 'k--')
    # plot the FPR and TPR for model
    plt.plot(fpr, tpr)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.show()

    auc_sc = roc_auc_score(y_test,y_scores[:,1])
    print('AUC: ' + str(auc_sc))

    return(mse, r2, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc)


def dataset_metro_sum(hurr_mod_data, gas_data):
    from datetime import datetime, timedelta, date, time
    import pandas as pd
    import numpy as np

    # select columns for configuring modeling parmeters
    dt_sel_data = hurr_mod_data[['SID','SEASON','NAME','START DATE','END DATE','ISO_TIME','DIST2LAND', 'LANDFALL','USA_LAT','USA_LON','USA_WIND','USA_SSHS','STORM_SPEED','STORM_DIR','DATE']]
    
    # list of storms in data set
    storm_list_ = dt_sel_data['NAME'].unique()
    storm_list = pd.DataFrame(storm_list_)
    storm_list.columns = ['NAME']
    
    dlist = []
    list_of_dfs = []
    c = 0
    
    s = len(storm_list)

    storm = storm_list['NAME'].iat[0]
    #print(storm)
    
    h_data = dt_sel_data[dt_sel_data['NAME'] == storm]
    h_data.reset_index(drop = True, inplace = True)
    
    D = h_data['DATE'].unique()
    #print(D)
    Dates =  pd.DataFrame(D)
    Dates.columns = ['DATE']
    
    Dates['DATE1'] = pd.to_datetime(Dates['DATE'])
    
    k = len(Dates)
    #print(k)
    
    start_date = (Dates['DATE1'].min())
    end_date = (Dates['DATE1'].max())
    
    mon_start = (Dates['DATE1'].min()).month
    mon_end = (Dates['DATE1'].max()).month
    #print(mon_start)
    #print(mon_end)
    
    max_cat = h_data['USA_SSHS'].max()
    #print(max_cat)

    stormname = []
    stormstart = []
    stormend = []
    startmon = []
    endmon = []
    stormdur = []
    stormcatmax = []
    
    for n in range(s):
        storm = storm_list['NAME'].iat[n]
        #print(storm)
        stormname.append(storm)
        
        h_data = dt_sel_data[dt_sel_data['NAME'] == storm]
        h_data.reset_index(drop = True, inplace = True)
        
        D = h_data['DATE'].unique()
        #print(D)
        Dates = pd.DataFrame(D)
        Dates.columns = ['DATE']
        
        Dates['DATE1'] = pd.to_datetime(Dates['DATE'])
        
        k = len(Dates)
        stormdur.append(k)
        
        start_date = (Dates['DATE1'].min())
        end_date = (Dates['DATE1'].max())
    
        stormstart.append(start_date)
        stormend.append(end_date)
        
        mon_start = (Dates['DATE1'].min()).month
        mon_end = (Dates['DATE1'].max()).month
        startmon.append(mon_start)
        endmon.append(mon_end)
        
        max_cat = h_data['USA_SSHS'].max()
        stormcatmax.append(max_cat)
    
    storm_sum_data = pd.DataFrame(stormname)
    storm_sum_data.columns = ['Name']
    storm_sum_data['Max Cat'] = stormcatmax
    storm_sum_data['Duration'] = stormdur
    storm_sum_data['Start Month'] = startmon
    storm_sum_data['Start Date'] = stormstart
    storm_sum_data['End Month'] = endmon
    storm_sum_data['End Date'] = stormend
    
    storm_sum_data.head()

    L = len(storm_sum_data)
    #gas_data = gas_data_redux
    
    dat_join = []
    storm = []
    met = []
    reg_start = []
    reg_end = []
    
    metro_name = []
    metro_all = ['Pensacola', 'Tallahassee', 'Tampa-St. Petersburg-Clearwater', 'Fort Myers-Cape Coral', 'Miami','West Palm Beach-Boca Raton','Melbourne-Titusville','Daytona Beach','Jacksonville']
    for n in range(L):
        sn = storm_sum_data['Name'].iloc[n]
        #print(sn)
        sd = storm_sum_data['Start Date'].iloc[n]
    
        ed = storm_sum_data['End Date'].iloc[n]
        
        for metro_sel in metro_all:
            #print(f'{metro_sel} selected')
            storm.append(storm_sum_data['Name'].iloc[n])
        
            h2_gas_data1 = gas_data[(gas_data['metro'] == metro_sel) & (gas_data['date'] == sd)]
            #print(h2_gas_data1)
        
            met.append(metro_sel)
    
            reg_st = h2_gas_data1['regular'].item()
            #print(sd)
            #print(reg_st)
    
            reg_start.append(reg_st)
            #print(reg_start)
        
            h2_gas_data2 = gas_data[(gas_data['metro'] == metro_sel) & (gas_data['date'] == ed)]
            #print(h2_gas_data2)
        
            reg_ed = h2_gas_data2['regular'].item()
            #print(ed)
            #print(reg_ed)
    
            reg_end.append(reg_ed)
        
        
    dat_join = pd.DataFrame(storm)
    dat_join.columns = ['Name']
    
    dat_join['Metro'] = met
    dat_join['Start Reg'] = reg_start
    dat_join['End Reg'] = reg_end
    
    dat_join['Gas_Chg'] = dat_join['End Reg'] - dat_join['Start Reg']
    
    dat_join['Gas_Chg_Pct'] = (dat_join['Gas_Chg']/dat_join['Start Reg'])

    data_comp = dat_join.merge(
        storm_sum_data,
        on = ['Name'],
        how = 'left')
    data_comp.head()
    
    data_for_dt = data_comp[['Gas_Chg_Pct','Max Cat','Duration','Start Month','End Month']]
    
    #data_for_dt.head()

    data_for_dt['buy'] = np.where(data_for_dt['Gas_Chg_Pct'] > 0, 1, 0)

    data_for_dt.drop(columns = ['Gas_Chg_Pct'], inplace = True)

    #data_for_dt.head()

    return data_for_dt
    