# dec_tree_fcns.py

# configure a test train split with option to stratify
def model_setup(model, y_param, testsplit=0.2, stratify_set = False):
    from sklearn.model_selection import train_test_split

    X = model.drop(y_param, axis=1)
    y = model[y_param]

    if stratify_set:
        X_train_bal, X_test_bal, y_train_bal, y_test_bal = train_test_split(X, y, test_size=testsplit, random_state=42,
                                                                        stratify=y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testsplit, random_state=42)

    features_list = X.columns.tolist()
    if stratify_set:
        return (X_train_bal, X_test_bal, y_train_bal, y_test_bal, X_train, X_test, y_train, y_test, features_list)
    else:
        return (X_train, X_test, y_train, y_test, features_list)


# generate decision tree model
def model_dec_tree(X_train, X_test, y_train, features_list, max_lvls=None, min_leaf_samp=1,
                   max_leaf_nod=None):
    import pandas as pd
    from sklearn import tree
    from sklearn.tree import DecisionTreeClassifier, plot_tree

    mod_dt = tree.DecisionTreeClassifier(criterion='entropy', random_state=42, max_depth=max_lvls,
                                         min_samples_leaf=min_leaf_samp, max_leaf_nodes=max_leaf_nod)
    mod_dt.fit(X_train, y_train)

    y_pred = mod_dt.predict(X_test)

    feat_list = features_list
    feat_imp = mod_dt.feature_importances_

    # plt.figure(figsize = (20,15))
    # plot_tree(mod_dt, filled = True, feature_names = feat_list, rounded = True)
    # plt.show()

    dtFeatures = pd.DataFrame({'Features': features_list, 'Importances': mod_dt.feature_importances_})
    print(dtFeatures.sort_values(by='Importances', ascending=False))

    return (mod_dt, y_pred, feat_list, feat_imp)

# generate decision tree model with figure and performance evaluation
def dec_tree_std(model, y_param, class_list, testsplit, max_lvls, min_leaf_samp, max_leaf_nod):
    import matplotlib.pyplot as plt
    from sklearn.tree import DecisionTreeClassifier, plot_tree
    X_train, X_test, y_train, y_test, features_list = model_setup(model,y_param,testsplit)

    mod_dt, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train, features_list, max_lvls, min_leaf_samp, max_leaf_nod)

    mse, r2, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test,y_pred,X_test,mod_dt)

    # plot decision tree
    plt.figure(figsize = (20,15))
    plot_tree(mod_dt, filled = True, feature_names = feat_list, class_names = class_list, rounded = True)
    plt.show()

# generate decision tree model with class weight balancing
def model_dec_tree_bal(X_train_bal, X_test, y_train_bal, features_list, max_lvls=None, min_leaf_samp=1,
                       max_leaf_nod=None):
    import pandas as pd
    from sklearn import tree
    from sklearn.tree import DecisionTreeClassifier, plot_tree

    mod_dtb = tree.DecisionTreeClassifier(criterion='entropy', random_state=42, max_depth=max_lvls,
                                          min_samples_leaf=min_leaf_samp, max_leaf_nodes=max_leaf_nod,
                                          class_weight='balanced')

    mod_dtb.fit(X_train_bal, y_train_bal)

    y_pred = mod_dtb.predict(X_test)

    feat_list = features_list
    feat_imp = mod_dtb.feature_importances_

    dtbFeatures = pd.DataFrame({'Features': features_list, 'Importances': mod_dtb.feature_importances_})
    print(dtbFeatures.sort_values(by='Importances', ascending=False))

    # plt.figure(figsize = (20,15))
    # plot_tree(mod_dt, filled = True, feature_names = feat_list, rounded = True)
    # plt.show()

    return (mod_dtb, y_pred, feat_list, feat_imp)

# generate balanced decision tree using stratification with figure and performance evaluation
def dec_tree_bal(model, y_param, class_list, testsplit, max_lvls, min_leaf_samp, max_leaf_nod):
    import matplotlib.pyplot as plt
    from sklearn.tree import DecisionTreeClassifier, plot_tree
    X_train_bal, X_test_bal, y_train_bal, y_test_bal, X_train, X_test, y_train, y_test, features_list = model_setup(model,y_param,testsplit,stratify_set = True)

    mod_dtb, y_pred, feat_list, feat_imp = model_dec_tree_bal(X_train_bal, X_test, y_train_bal, features_list, max_lvls, min_leaf_samp, max_leaf_nod)

    mse, r2, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test,y_pred,X_test,mod_dtb)

    # plot decision tree
    plt.figure(figsize = (20,15))
    plot_tree(mod_dtb, filled = True, feature_names = feat_list, class_names = class_list, rounded = True)
    plt.show()


def model_stats_analysis(y_test, y_pred, X_test, model):
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, \
        classification_report, confusion_matrix, roc_auc_score, roc_curve

    # compute performance on test set
    mse = mean_squared_error(y_test, y_pred)
    print("Mean Squared Error: ", mse)

    r2 = r2_score(y_test, y_pred)
    print("R-squared: ", r2)

    acc_sc = accuracy_score(y_test, y_pred)
    # print('accuracy score: %.2f' % acc_sc)

    prec_sc = precision_score(y_test, y_pred, zero_division=np.nan)
    # print('precision score: %.2f' % prec_sc)

    rec_sc = recall_score(y_test, y_pred)
    # print('recall score: %.2f' % rec_sc)

    f1_sc = f1_score(y_test, y_pred)
    # print('f1 score: %.2f' % f1_sc)

    class_rep = classification_report(y_test, y_pred, labels=None, target_names=None, sample_weight=None, digits=2,
                                      output_dict=False, zero_division=np.nan)
    print(class_rep)

    conf_mat = confusion_matrix(y_test, y_pred, labels=None, sample_weight=None, normalize=None)
    # print(conf_mat)

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
    fpr, tpr, thresholds = roc_curve(y_test, y_scores[:, 1])

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

    auc_sc = roc_auc_score(y_test, y_scores[:, 1])
    print('AUC: ' + str(auc_sc))

    return (mse, r2, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc)


# parametric evaluation of decision tree hyperparameters
def dt_param(model, y_param, max_lvl_set, min_leaf_set, max_node_set):
    import pandas as pd

    # placeholders
    dt_results = []
    dat = []
    mse = []
    r2 = []
    acc = []
    prec = []
    rec = []
    f1 = []
    auc = []

    c = 0

    # model = model_all_avg
    # y_param = 'buy_avg'

    for i in max_lvl_set:
        for j in min_leaf_set:
            for k in max_node_set:
                c = c + 1

                mod_name = 'model' + '_' + str(c) + '_' + str(i) + '_' + str(j) + '_' + str(k)

                print(f"Model: {mod_name} ({c}) / Response: {y_param}")

                # Set up train and test data sets
                X_train, X_test, y_train, y_test, features_list = model_setup(model, y_param, testsplit=0.2)

                # Generate model
                mod_dt, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train,
                                                                     features_list, i, j, k)

                # Analyze model
                mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test,
                                                                                             mod_dt)

                dat.append(mod_name)
                mse.append(mse_sc)
                r2.append(r2_sc)
                acc.append(acc_sc)
                prec.append(prec_sc)
                rec.append(rec_sc)
                f1.append(f1_sc)
                auc.append(auc_sc)

    dt_results = pd.DataFrame(dat)
    dt_results.columns = ['data_model']
    # dt_results['data_model'] = dat
    dt_results['mse'] = mse
    dt_results['r2'] = r2
    dt_results['acc'] = acc
    dt_results['prec'] = prec
    dt_results['rec'] = rec
    dt_results['f1'] = f1
    dt_results['auc'] = auc

    print(dt_results)
    return dt_results

# evaluate decision trees for group of dataset models
def loop_dec_tree(model_list, model_names, class_list, y_param, max_lvls, min_leaf_samp, max_leaf_nod):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn import tree
    from sklearn.tree import DecisionTreeClassifier, plot_tree
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, \
        classification_report, confusion_matrix, roc_auc_score, roc_curve

    # placeholders
    dt_results = []

    dat = []
    mse = []
    r2 = []
    acc = []
    prec = []
    rec = []
    f1 = []
    auc = []

    # Loop to evaluate list of models
    for m in range(len(model_list)):
        model = model_list[m]
        mod_name = model_names[m]
        # if m< 8:
        #    y_param = y_param_list[m%2]
        # else:
        #    y_param = y_param_list[0]
        print(f"Model: {mod_name} ({m + 1}) / Response: {y_param}")

        # Set up train and test data sets
        X_train, X_test, y_train, y_test, features_list = model_setup(model, y_param, testsplit=0.2)

        # Generate model
        mod_dt, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train, y_test, y_param, features_list,
                                                             max_lvls, min_leaf_samp, max_leaf_nod)

        # Analyze model
        mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test, mod_dt)

        dat.append(mod_name)
        mse.append(mse_sc)
        r2.append(r2_sc)
        acc.append(acc_sc)
        prec.append(prec_sc)
        rec.append(rec_sc)
        f1.append(f1_sc)
        auc.append(auc_sc)

        # plot decision tree
        plt.figure(figsize=(20, 15))
        plot_tree(mod_dt, filled=True, feature_names=feat_list, class_names=class_list, rounded=True)
        plt.show()

        # plot count of distribution of buy / no buy
        plt.subplots(1, 3, figsize=(15, 3))
        plt.subplot(1, 3, 1)

        # Plot distribution in training data
        sns.countplot(x=y_train)
        plt.suptitle(f'Distribution of Not Buy / Buy for Decision Tree Model: {mod_name} & Response: {y_param}')
        plt.xlabel('Training Data')
        plt.xticks(fontsize=8)
        plt.ylabel('')

        plt.subplot(1, 3, 2)
        # Plot distribution in test data
        sns.countplot(x=y_test)
        # plt.title(f'')
        plt.xlabel('Test Data')
        plt.xticks(fontsize=8)
        plt.ylabel('')

        plt.subplot(1, 3, 3)
        # Plot distribution in predition data
        sns.countplot(x=y_pred)
        # plt.title(f'')
        plt.xlabel('Prediction Data')
        plt.xticks(fontsize=8)
        plt.ylabel('')
        plt.show()

    dt_results = pd.DataFrame(dat)
    dt_results.columns = ['data_model']
    # dt_results['data_model'] = dat
    dt_results['mse'] = mse
    dt_results['r2'] = r2
    dt_results['acc'] = acc
    dt_results['prec'] = prec
    dt_results['rec'] = rec
    dt_results['f1'] = f1
    dt_results['auc'] = auc

    print(dt_results)

# evaluate decision tree model with varying hyperparameters
def model_dec_tree_hyp_par_eval(model_list, model_names, class_list, y_param, max_lvls, min_leaf, max_leaf_nod, m=0):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn import tree
    from sklearn.tree import DecisionTreeClassifier, plot_tree

    dt_hpt_results = []

    dat = []
    mse = []
    r2 = []
    acc = []
    prec = []
    rec = []
    f1 = []
    auc = []
    lvl = []
    leaf = []
    node = []

    # m = 0
    model = model_list[m]
    mod_name = model_names[m]
    # y_param = y_param_list[0]
    print(f"Model: {mod_name} ({m + 1}) / Response: {y_param}")

    X_train, X_test, y_train, y_test, features_list = model_setup(model, y_param, testsplit=0.2)

    for max_lvls_v in range(2, 20, 2):
        # min_leaf = 5

        print(
            f"Model: {mod_name} ({m + 1}) / Response: {y_param} / max level: {max_lvls_v} / min leaf: {min_leaf} / max leaf node: {max_leaf_nod}")

        mod_dt, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train, features_list,
                                                             max_lvls_v, min_leaf, max_leaf_nod)

        mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test, mod_dt)

        dat.append(mod_name)
        lvl.append(max_lvls_v)
        leaf.append(min_leaf)
        node.append(max_leaf_nod)
        mse.append(mse_sc)
        r2.append(r2_sc)
        acc.append(acc_sc)
        prec.append(prec_sc)
        rec.append(rec_sc)
        f1.append(f1_sc)
        auc.append(auc_sc)

    for min_leaf_v in range(2, 20, 2):
        # max_lvls = 5

        print(
            f"Model: {mod_name} ({m + 1}) / Response: {y_param} / max level: {max_lvls} / min leaf: {min_leaf_v} / max leaf node: {max_leaf_nod}")

        mod_dt, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train, features_list,
                                                             max_lvls, min_leaf_v, max_leaf_nod)

        mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test, mod_dt)

        dat.append(mod_name)
        lvl.append(max_lvls)
        leaf.append(min_leaf_v)
        node.append(max_leaf_nod)
        mse.append(mse_sc)
        r2.append(r2_sc)
        acc.append(acc_sc)
        prec.append(prec_sc)
        rec.append(rec_sc)
        f1.append(f1_sc)
        auc.append(auc_sc)

    for max_leaf_v in range(2, 20, 2):
        # min_leaf = 5

        print(
            f"Model: {mod_name} ({m + 1}) / Response: {y_param} / max level: {max_lvls} / min leaf: {min_leaf} / max leaf node: {max_leaf_v}")

        mod_dt, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train, features_list,
                                                             max_lvls, min_leaf, max_leaf_v)

        mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test, mod_dt)

        dat.append(mod_name)
        lvl.append(max_lvls)
        leaf.append(min_leaf)
        node.append(max_leaf_v)
        mse.append(mse_sc)
        r2.append(r2_sc)
        acc.append(acc_sc)
        prec.append(prec_sc)
        rec.append(rec_sc)
        f1.append(f1_sc)
        auc.append(auc_sc)

    dt_hpt_results = pd.DataFrame(dat)
    dt_hpt_results.columns = ['data_model']

    dt_hpt_results['max_lvl'] = lvl
    dt_hpt_results['leaf'] = leaf
    dt_hpt_results['leafnode'] = node

    # dt_results['data_model'] = dat
    dt_hpt_results['mse'] = mse
    dt_hpt_results['r2'] = r2
    dt_hpt_results['acc'] = acc
    dt_hpt_results['prec'] = prec
    dt_hpt_results['rec'] = rec
    dt_hpt_results['f1'] = f1
    dt_hpt_results['auc'] = auc

    print(dt_hpt_results)

    # plot results
    # plot Impact of Variation of Decision Tree Max Level
    plt.subplots(3, 3, figsize=(20, 10))
    plt.subplot(3, 3, 1)
    #
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='mse')
    plt.suptitle(f'Impact of Variation of Decision Tree Max Level: {mod_name} & Response: {y_param}')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('mse')

    plt.subplot(3, 3, 2)
    #
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='r2')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('r2')

    plt.subplot(3, 3, 3)
    #
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='f1')
    # plt.title(f'')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('f1')

    plt.subplot(3, 3, 4)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='acc')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('accuracy')

    plt.subplot(3, 3, 5)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='prec')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('precision')

    plt.subplot(3, 3, 6)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='rec')
    # plt.title(f'')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('recall')

    plt.subplot(3, 3, 7)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='auc')
    # plt.title(f'')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('area under ROC curve')

    # plot Impact of Variation of Decision Tree Max Leaf Samples
    plt.subplots(3, 3, figsize=(20, 10))
    plt.subplot(3, 3, 1)
    #
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='mse')
    plt.suptitle(f'Impact of Variation of Decision Tree Min Leaf Samples: {mod_name} & Response: {y_param}')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('mse')

    plt.subplot(3, 3, 2)
    #
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='r2')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('r2')

    plt.subplot(3, 3, 3)
    #
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='f1')
    # plt.title(f'')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('f1')

    plt.subplot(3, 3, 4)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='acc')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('accuracy')

    plt.subplot(3, 3, 5)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='prec')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('precision')

    plt.subplot(3, 3, 6)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='rec')
    # plt.title(f'')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('recall')

    plt.subplot(3, 3, 7)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='auc')
    # plt.title(f'')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('area under ROC curve')

    # plot Impact of Variation of Decision Tree Max Leaf Nodes
    plt.subplots(3, 3, figsize=(20, 10))
    plt.subplot(3, 3, 1)
    #
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='mse')
    plt.suptitle(f'Impact of Variation of Decision Tree Max Leaf Nodes: {mod_name} & Response: {y_param}')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('mse')

    plt.subplot(3, 3, 2)
    #
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='r2')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('r2')

    plt.subplot(3, 3, 3)
    #
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='f1')
    # plt.title(f'')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('f1')

    plt.subplot(3, 3, 4)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='acc')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('accuracy')

    plt.subplot(3, 3, 5)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='prec')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('precision')

    plt.subplot(3, 3, 6)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='rec')
    # plt.title(f'')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('recall')

    plt.subplot(3, 3, 7)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='auc')
    # plt.title(f'')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('area under ROC curve')


def model_dec_tree_bal_hyp_par_eval(model_list, model_names, class_list, y_param, max_lvls, min_leaf, max_leaf_nod,
                                    m=0):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn import tree
    from sklearn.tree import DecisionTreeClassifier, plot_tree

    dt_hpt_results = []

    dat = []
    mse = []
    r2 = []
    acc = []
    prec = []
    rec = []
    f1 = []
    auc = []
    lvl = []
    leaf = []
    node = []

    # m = 0
    model = model_list[m]
    mod_name = model_names[m]
    # y_param = y_param_list[0]
    print(f"Balanced Model: {mod_name} ({m + 1}) / Response: {y_param}")

    X_train_bal, X_test_bal, y_train_bal, y_test_bal, X_train, X_test, y_train, y_test, features_list = model_setup(
        model, y_param, testsplit=0.2,stratify_set = True)

    for max_lvls_v in range(2, 20, 2):
        # min_leaf = 5

        print(
            f"Balanced Model: {mod_name} ({m + 1}) / Response: {y_param} / max level: {max_lvls_v} / min leaf: {min_leaf} / max leaf node: {max_leaf_nod}")

        mod_dtb, y_pred, feat_list, feat_imp = model_dec_tree_bal(X_train_bal, X_test, y_train_bal,
                                                                  features_list, max_lvls_v, min_leaf, max_leaf_nod)

        mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test, mod_dtb)

        dat.append(mod_name)
        lvl.append(max_lvls_v)
        leaf.append(min_leaf)
        node.append(max_leaf_nod)
        mse.append(mse_sc)
        r2.append(r2_sc)
        acc.append(acc_sc)
        prec.append(prec_sc)
        rec.append(rec_sc)
        f1.append(f1_sc)
        auc.append(auc_sc)

    for min_leaf_v in range(2, 20, 2):
        # max_lvls = 5

        print(
            f"Balanced Model: {mod_name} ({m + 1}) / Response: {y_param} / max level: {max_lvls} / min leaf: {min_leaf_v} / max leaf node: {max_leaf_nod}")

        mod_dtb, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train, features_list,
                                                             max_lvls, min_leaf_v, max_leaf_nod)

        mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test, mod_dtb)

        dat.append(mod_name)
        lvl.append(max_lvls)
        leaf.append(min_leaf_v)
        node.append(max_leaf_nod)
        mse.append(mse_sc)
        r2.append(r2_sc)
        acc.append(acc_sc)
        prec.append(prec_sc)
        rec.append(rec_sc)
        f1.append(f1_sc)
        auc.append(auc_sc)

    for max_leaf_v in range(2, 20, 2):
        # min_leaf = 5

        print(
            f"Balanced Model: {mod_name} ({m + 1}) / Response: {y_param} / max level: {max_lvls} / min leaf: {min_leaf} / max leaf node: {max_leaf_v}")

        mod_dtb, y_pred, feat_list, feat_imp = model_dec_tree(X_train, X_test, y_train, features_list,
                                                             max_lvls, min_leaf, max_leaf_v)

        mse_sc, r2_sc, acc_sc, prec_sc, rec_sc, f1_sc, auc_sc = model_stats_analysis(y_test, y_pred, X_test, mod_dtb)

        dat.append(mod_name)
        lvl.append(max_lvls)
        leaf.append(min_leaf)
        node.append(max_leaf_v)
        mse.append(mse_sc)
        r2.append(r2_sc)
        acc.append(acc_sc)
        prec.append(prec_sc)
        rec.append(rec_sc)
        f1.append(f1_sc)
        auc.append(auc_sc)

    dt_hpt_results = pd.DataFrame(dat)
    dt_hpt_results.columns = ['data_model']

    dt_hpt_results['max_lvl'] = lvl
    dt_hpt_results['leaf'] = leaf
    dt_hpt_results['leafnode'] = node

    # dt_results['data_model'] = dat
    dt_hpt_results['mse'] = mse
    dt_hpt_results['r2'] = r2
    dt_hpt_results['acc'] = acc
    dt_hpt_results['prec'] = prec
    dt_hpt_results['rec'] = rec
    dt_hpt_results['f1'] = f1
    dt_hpt_results['auc'] = auc

    print(dt_hpt_results)

    # plot results
    # plot Impact of Variation of Decision Tree Max Level
    plt.subplots(3, 3, figsize=(20, 10))
    plt.subplot(3, 3, 1)
    #
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='mse')
    plt.suptitle(f'Impact of Variation of Decision Tree Max Level: {mod_name} & Response: {y_param} (Balanced)')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('mse')

    plt.subplot(3, 3, 2)
    #
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='r2')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('r2')

    plt.subplot(3, 3, 3)
    #
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='f1')
    # plt.title(f'')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('f1')

    plt.subplot(3, 3, 4)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='acc')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('accuracy')

    plt.subplot(3, 3, 5)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='prec')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('precision')

    plt.subplot(3, 3, 6)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='rec')
    # plt.title(f'')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('recall')

    plt.subplot(3, 3, 7)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[0:8], x='max_lvl', y='auc')
    # plt.title(f'')
    plt.xlabel('max level')
    plt.xticks(fontsize=8)
    plt.ylabel('area under ROC curve')

    # plot Impact of Variation of Decision Tree Max Leaf Samples
    plt.subplots(3, 3, figsize=(20, 10))
    plt.subplot(3, 3, 1)
    #
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='mse')
    plt.suptitle(f'Impact of Variation of Decision Tree Min Leaf Samples: {mod_name} & Response: {y_param} (Balanced)')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('mse')

    plt.subplot(3, 3, 2)
    #
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='r2')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('r2')

    plt.subplot(3, 3, 3)
    #
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='f1')
    # plt.title(f'')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('f1')

    plt.subplot(3, 3, 4)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='acc')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('accuracy')

    plt.subplot(3, 3, 5)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='prec')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('precision')

    plt.subplot(3, 3, 6)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='rec')
    # plt.title(f'')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('recall')

    plt.subplot(3, 3, 7)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[9:17], x='leaf', y='auc')
    # plt.title(f'')
    plt.xlabel('min leaf samples')
    plt.xticks(fontsize=8)
    plt.ylabel('area under ROC curve')

    # plot Impact of Variation of Decision Tree Max Leaf Nodes
    plt.subplots(3, 3, figsize=(20, 10))
    plt.subplot(3, 3, 1)
    #
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='mse')
    plt.suptitle(f'Impact of Variation of Decision Tree Max Leaf Nodes: {mod_name} & Response: {y_param} (Balanced)')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('mse')

    plt.subplot(3, 3, 2)
    #
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='r2')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('r2')

    plt.subplot(3, 3, 3)
    #
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='f1')
    # plt.title(f'')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('f1')

    plt.subplot(3, 3, 4)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='acc')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('accuracy')

    plt.subplot(3, 3, 5)
    # Plot distribution in training data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='prec')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('precision')

    plt.subplot(3, 3, 6)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='rec')
    # plt.title(f'')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('recall')

    plt.subplot(3, 3, 7)
    # Plot distribution in test data
    sns.lineplot(data=dt_hpt_results[18:26], x='leafnode', y='auc')
    # plt.title(f'')
    plt.xlabel('max leaf nodes')
    plt.xticks(fontsize=8)
    plt.ylabel('area under ROC curve')
