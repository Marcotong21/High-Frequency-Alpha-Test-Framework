import pandas as pd
import time


# Import 3 py files for the modules of data processing, factor generation, and performance analysis respectively
import Data_Process
import factors
import performance_analysis
import config


start_time = time.time()
######################### STEP1:  Read the data and process it initially  ###################################

factor_list = config.factor_list


# month = config.month
usage = config.usage       # 'test' or 'all', one/two day test or all data

if usage == 'all':
    # Read all csv's in the folder and concat as total data
    l2 = Data_Process.read_data('ss_raw_data')
elif usage == 'test':
    # Use one/two day of data as a test
    l2 = pd.read_csv('ss_raw_data/20230303.csv')
    # l2_2 = pd.read_csv('ss_raw_data/20230306.csv')
    # l2 = pd.concat([l2_1, l2_2], ignore_index=True)
# else:
#     l2 = Data_Process.read_data('ss_raw_data')
#     l2 = l2[l2['TradingDay'].str.slice(start=5, stop=7).isin(['04'])]




# Data processing, mainly removing unneeded columns, and setting the dateframe index
data= Data_Process.clean_l2_data(l2)
# Index range for filtering factor calculation:
# e.g. exclude the first n seconds of the open and the last n seconds before the close.
# Timestamps at the beginning of the opening can interfere with the signal during moving averages,
#  while it may not be possible to place an order at the close time.
factor_index = Data_Process.factor_time_range(data.index, n1=config.n1, n2=config.n2)  # (n1 n2 can be changed)


######################### STEP2: Calculate factor values ###################################

# Call factors.py to get factor values dataframe
factor = factors.get_alpha(data, factor_index, factor_list)

# Factor processing, including normalization and processing inf,nan
factor = Data_Process.pretreat_factor(factor, data)


######################### STEP3: Factor Analysis ###################################

# Calculate the ic value for each factor, and the corr between the factors.
# The output is in the results folder
performance_analysis.IC_quantile(factor)
# Quartile y-mean plots, statistical distributions for each factor
# The output is in results/factor folder

# ACF plot not enabled yet
performance_analysis.output(factor)




################### STEP4: Storage factor value #####################
# It would be too cumbersome to calculate all the factors each time, so store all the processed factors.
if len(data) > 200000:
    # train[factor_columns].to_pickle('train_factors.pkl')
    factor.to_pickle('factors.pkl')




end_time = time.time()
run_time = end_time - start_time
print(f"program runtime：{run_time} seconds")
