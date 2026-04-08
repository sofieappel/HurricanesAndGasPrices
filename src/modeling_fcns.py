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


def cluster(df, k, features = None, plot = True):
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    import pandas as pd
    import plotly.express as px

    # Select numeric features if not provided
    if features is not None:
        df_model = df[features].copy()
    else:
        df_model = df.select_dtypes(include='number').copy()

    # Scale
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df_model),
                             columns=df_model.columns)

    # KMeans
    kmeans = KMeans(n_clusters=k,
                    init='k-means++',
                    max_iter=300,
                    n_init=10,
                    random_state=0)
    labels = kmeans.fit_predict(df_scaled)

    # Adding labels back to original
    df_result = df.copy()
    df_result['cluster'] = labels

    # Centroids
    centroids = pd.DataFrame(kmeans.cluster_centers_, columns=df_model.columns)
    centroids['cluster'] = centroids.index

        # Metrics
    silhouette = silhouette_score(df_scaled, labels)

        # Parallel plot
    if plot:
        fig = px.parallel_coordinates(
                df_result,
                dimensions=df_model.columns,
                color='cluster',
                color_continuous_scale=px.colors.sequential.Viridis)
        fig.show()

    return {
        'data': df_result,
        'centroids': centroids,
        'model': kmeans,
        'scaler': scaler,
        'silhouette': silhouette
        }
