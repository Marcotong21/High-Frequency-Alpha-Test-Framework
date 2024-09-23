import pandas as pd
import numpy as np
import os
import config

def read_data(folder_path):
    """
        Read all the csv's in the folder, concat together
    :param folder_path:
    :return: all data
    """
    files = os.listdir(folder_path)
    dataframes = []
    # Iterate through the list of filenames, filter out the CSV files, and read the
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            dataframes.append(df)
    # concat merges all DataFrames
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df


def clean_l2_data(l2):
    """
        Usage:
        1.merge date and time and set index to datetime format
        2.drop some useless columns
    :param l2: level2数据
    :return: 处理后的数据
    """
    l2['UpdateMillisec_str'] = l2['UpdateMillisec'].astype(str).str.zfill(3)
    # Merge the time string and the milliseconds string to create a new indexed column
    l2['combined_index'] = l2['UpdateTime'] + '.' + l2['UpdateMillisec_str']
    # Set 'combined_index' to index and convert to datetime type
    l2.set_index('combined_index', inplace=True)
    l2.index = pd.to_datetime(l2.index)

    # drop some useless columns
    l2.drop(columns=['InstrumentID', 'UpdateMillisec','ExchangeID', 'time_sec', 'temp2'] ,inplace=True)
    # Prevent multiple csv's from being out of order when concatting
    l2_sorted = l2.sort_index()

    # When volume is 0, Lastprice is empty; just fill in the missing values.
    l2_sorted['Volume'] = l2_sorted['Volume'].fillna(method='bfill')

    # It's just filled with nan so that the calculation doesn't report an error, it doesn't affect the actual factor value.
    l2_sorted['BidVolume1'] = l2_sorted['BidVolume1'].fillna(method='bfill')
    l2_sorted['AskVolume1'] = l2_sorted['AskVolume1'].fillna(method='bfill')
    l2_sorted['BidPrice1'] = l2_sorted['BidPrice1'].fillna(method='bfill')
    l2_sorted['AskPrice1'] = l2_sorted['AskPrice1'].fillna(method='bfill')

    return l2_sorted


def factor_time_range(index, n1, n2):
    """
        Range of index for filter factor calculation
    :param index: index of the data, in datetime format
    :param n1: the number of seconds before the opening of the market to be eliminated,
                e.g. n1=30 seconds for the opening of the market to be eliminated
    :param n2: the number of seconds after the close of the market to be culled,
                e.g., n2=10 seconds for the open.
    :return: the culled indexes, which can be used to calculate the factors
    """
    # night
    night_start = '21:00:00'
    night_end = '01:00:00'         # todo：For different underlying, the night market closes at different times
    # morning 1
    morning_start = '09:00:00'
    morning_end = '10:15:00'
    # morning 2
    late_morning_start = '10:30:00'
    late_morning_end = '11:30:00'
    # afternoon
    afternoon_start = '13:30:00'
    afternoon_end = '15:00:00'

    # Define the n-second timedelta object
    n_seconds = pd.to_timedelta(f'{n1} seconds')
    n2_seconds = pd.to_timedelta(f'{n2} seconds')
    n3_seconds = pd.to_timedelta(f'{config.open_minutes} seconds')

    # Construct filters Retain the index that satisfies the condition,
    # i.e., retain: n1 seconds from the opening of the market to n2 seconds before the closing of the market
    conditions_to_keep = (
            ((index.time >= (pd.to_datetime(night_start) + n_seconds).time()) |     # todo: note here: if the night close is after 24:00, the last symbol is |; if the close is before 24:00, it is &
             (index.time <= (pd.to_datetime(night_end) - n2_seconds).time())) |
            ((index.time >= (pd.to_datetime(morning_start) + n_seconds).time()) &
             (index.time <= (pd.to_datetime(morning_end) - n2_seconds).time())) |
            ((index.time >= (pd.to_datetime(late_morning_start) + n_seconds).time()) &
             (index.time <= (pd.to_datetime(late_morning_end) - n2_seconds).time())) |
            ((index.time >= (pd.to_datetime(afternoon_start) + n_seconds).time()) &
             (index.time <= (pd.to_datetime(afternoon_end) - n2_seconds).time()))
    )
    # Apply filters
    index_filtered = index[conditions_to_keep]

    if config.divide_time_range:
        # Only keep the opening minutes
        conditions_to_keep1 = (
                ((index.time <= (pd.to_datetime(night_start) + n3_seconds).time()) &
                 (index.time >= pd.to_datetime(night_start).time())) |
                ((index.time <= (pd.to_datetime(morning_start) + n3_seconds).time()) &
                 (index.time >= (pd.to_datetime(morning_start)).time())) |
                ((index.time <= (pd.to_datetime(afternoon_start) + n3_seconds).time()) &
                 (index.time >= (pd.to_datetime(afternoon_start)).time())))

        index_filtered = index[conditions_to_keep1 & conditions_to_keep]

    return index_filtered


def pretreat_factor(value0, data):
    """
        Factor processing
        First, set all the factor values within the stopping range to nan, because it is impossible to open a position at this time, and need to be eliminated.
        Then calculate the mean and variance after removing inf and nan, and then replace inf and nan with the mean;
        Then standardize the factors
    :param factor_df:
    :return:
    """
    value = value0.copy(deep=True)

    # Remove up and down stops in the training and test sets
    value = remove_limit(value, data)

    # standardization
    value = standardize(value)
    # MAD depolarization (not enabled)
    if config.extreme_value:
        value = extreme_process_MAD(value)
    return value


def standardize(value):
    """
        Setting the factor values of nan and inf to mean and then normalizing the factor values.
    :param data:
    :return:
    """
    factor_stock = value.columns.difference(['y'])
    for stock in factor_stock:
        x = value[stock]

        # Calculate mean and std after deleting nan and inf
        finite_values = x[np.isfinite(x)]
        values = finite_values.dropna()
        mean = values.mean()
        std = values.std()

        # Fill the values of nan and inf with mean
        x = x.fillna(mean)
        x = x.replace([np.inf, -np.inf], mean)

        value[stock] = (x - mean)/std
    return value


# Median to extremes, using MAD
def extreme_process_MAD(value):
    factor_stock = value.columns.difference(['y'])
    for stock in factor_stock:
        x = value[stock]
        median = x.median()
        MAD = abs(x - median).median()
        x[x>(median+3*1.4826*MAD)] = median+3*1.4826*MAD
        x[x<(median-3*1.4826*MAD)] = median-3*1.4826*MAD
        value[stock] = x
    return value


def remove_limit(factor_df, data0):
    """
        Find the time points for up and down stops, and set the factor values for all of these time points to nan
    :param factor_df:
    :param data0:
    :return:
    """
    data = data0.copy()
    factor_column = factor_df.columns.difference(['y'])
    # Screening for up and down stops
    # time_points = data[(data['BidPrice1'] == 0) | (data['BidPrice1'] == np.nan) | (data['AskPrice1'] == np.nan) | (data['AskPrice1'] == 0)].index
    # Out of 10 price, as long as one of them is empty it will be considered as an up or down stop
    bid_cols = [col for col in data.columns if col.startswith('BidPrice')]
    ask_cols = [col for col in data.columns if col.startswith('AskPrice')]
    conditions = [(data[col] == 0) | (data[col].isna()) for col in bid_cols + ask_cols]
    combined_condition = np.any(conditions, axis=0)
    time_points = data[combined_condition].index

    matching_indices = time_points.intersection(factor_df.index)
    # set to nan. nan will be handled subsequently
    factor_df.loc[matching_indices, factor_column] = np.nan

    return factor_df







