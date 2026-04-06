# modeling_fcns.py

def model_setup(model,y_param,testsplit):
    from sklearn.model_selection import train_test_split
    
    X = model.drop(y_param, axis = 1)
    y = model[y_param]
    
    X_train, X_test, y_train, y_test =  train_test_split(X, y, test_size = testsplit, random_state = 42)

    features_list = X.columns.tolist()

    return(X_train, X_test, y_train, y_test, features_list)


def model_lin_reg(X_train, X_test, y_train, y_test):
    from sklearn.linear_model import LinearRegression
    import statsmodels.api as sm

    X_train = sm.add_constant(X_train)

    model = sm.OLS(y_train, X_train).fit()

    m_sum = model.summary()

    m_pval = model.pvalues

    return(model, m_sum, m_pval)
    

def model_dec_tree():
    x

def model_rand_forest():
    x


def cluster(df, k):
    #Scale features of numeric dataframe
    df = df.select_dtypes(['number'])
    scaler = StandardScaler()
    df = pd.DataFrame(scaler.fit_transform(df),columns=df.columns)

    kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(df)
    features = ['MAX CAT', 'STORM DURATION','gas_pct_change']

    # Adding cluster labels to the dataframe
    df_centroids = pd.DataFrame(kmeans.cluster_centers_, columns=features)
    df_centroids['cluster'] = df_centroids.index

    fig = px.parallel_coordinates(df_centroids, color='cluster', color_continuous_scale=px.colors.sequential.Viridis)
    fig.show()
