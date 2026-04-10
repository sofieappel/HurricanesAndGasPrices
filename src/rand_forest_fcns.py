# rand_forest_fcns.py

def model_rand_forest(X_train, X_test, y_train, y_test, y_param, features_list, n_est=100, max_lvls=5, min_leaf_samp=5,
                      min_samp_splt=2):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score

    mod_rf = RandomForestClassifier(
        n_estimators=n_est,
        max_depth=max_lvls,
        min_samples_leaf=min_leaf_samp,
        min_samples_split=min_samp_splt,
        random_state=42,
        oob_score=True
    )

    mod_rf.fit(X_train, y_train)

    y_pred = mod_rf.predict(X_test)

    oob_score = mod_rf.oob_score_
    print("Out-of-Bag Score: ", oob_score)

    feat_list = features_list
    feat_imp = mod_rf.feature_importances_
    dfFeatures = pd.DataFrame({'Features': features_list, 'Importances': mod_rf.feature_importances_})
    print(dfFeatures.sort_values(by='Importances', ascending=False))

    print(f"Number of trees in random forest: {len(mod_rf.estimators_)}")

    return (mod_rf, y_pred, oob_score, feat_list, feat_imp)