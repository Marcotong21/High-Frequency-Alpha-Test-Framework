import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import skew, kurtosis

def get_alpha(data, factor_index, factor_list):
    """

    :param data: Processed raw data
    :param factor_index: The remaining index after filtering
    :param factor_list: The list of factors needed to compute the value
    :return:
    """

    current = pd.DataFrame()
    current.index = pd.to_datetime(current.index)

    for single_factor in factor_list:
        if single_factor not in current.columns:
            func = globals()[single_factor]
            value = func(data)
            # Add the factor value to the factor dataset of current
            current.insert(0, single_factor, value)

    # insert y to the dataframe
    current['y'] = data['y_pos'].loc[current.index] * 10000 # unit is bp

    # Remove a couple ticks at open and close
    current = current.loc[factor_index]

    # Check the factor value output for the presence of nan or inf, if so print the factor name
    problem_columns = list(set(current.columns[current.isna().any()].tolist() + current.columns[np.isinf(current).any()].tolist()))
    if problem_columns:
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!{problem_columns}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    return current


#################### Of course I will not upload my alphas on github! :-) ############################
#################### Here I only put two simple alphas as example  ###################################

def z(data0):
    data = data0.copy()

    return np.log((data['BidPrice1'] + data['AskPrice1']) / 2) - np.log(data['LastPrice'])


def imbalance(data0, n=8):
    data = data0.copy()
    bid_sum_volume = data[['BidVolume1', 'BidVolume2', 'BidVolume3', 'BidVolume4', 'BidVolume5']].sum(axis=1)
    ask_sum_volume = data[['AskVolume1', 'AskVolume2', 'AskVolume3', 'AskVolume4', 'AskVolume5']].sum(axis=1)
    imbalance = np.log(bid_sum_volume / ask_sum_volume)
    return imbalance - imbalance.rolling(n).mean()