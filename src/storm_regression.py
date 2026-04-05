import pandas as pd 
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def storm_ols(df, storm_name, outcome, regressors, diagnostic=True, dropna=True):
    # set ups 
    df = df.copy()

    df["name"] = df["name"].astype(str).str.strip()
    storm_name = str(storm_name).strip()

    reg_df = df[df["name"] == storm_name].copy()

    if reg_df.empty:
        raise ValueError(f"no rows for the storm. wrong name. You said {storm_name}")
    
    reg_df = reg_df[[outcome] + regressors].copy()

    na_counts = reg_df.isna().sum()
    total_nam = na_counts.sum()

    if total_nam > 0:
        if dropna == True:
            reg_df = reg_df.dropna()
    
    # modeling 
    y = reg_df[outcome]
    X = reg_df[regressors]
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()
    print(model.summary())

    if diagnostic == True:
        fitted = model.fittedvalues
        residuals = model.resid 
        # residuals vs fitted. hope random around 0  
        plt.scatter(fitted, residuals, alpha = .6)
        plt.title(f'Residuals vs Fitted for {storm_name}')
        plt.show()

    return model, reg_df 


def ols_train_test(df, metro_name, outcome, regressors, test_size):
    metro_df = df[df["met"] == metro_name].copy()

    model_df = metro_df[[outcome] + regressors].dropna().copy()
    
    X = model_df[regressors]
    y = model_df[outcome]

    print("Rows in model_df:", len(model_df))
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=test_size 
    )

    X_train = sm.add_constant(X_train)
    X_test = sm.add_constant(X_test)

    model = sm.OLS(y_train, X_train).fit()

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    performance_df = pd.DataFrame({
        "observations" : [len(model_df)],
        "observations in train": [len(X_train)],
        "observations in test" : [len(X_test)],
        "train_rmse": [np.sqrt(mean_squared_error(y_train, y_train_pred))],
        "test_rmse": [np.sqrt(mean_squared_error(y_test, y_test_pred))],
        "train_r2": [r2_score(y_train, y_train_pred)],
        "test_r2": [r2_score(y_test, y_test_pred)],
    })

    performance_df = performance_df.T
    print(performance_df)

    return model, performance_df