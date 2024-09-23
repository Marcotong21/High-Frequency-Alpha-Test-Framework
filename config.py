#### SS ####


### Configure all variable parameters


# current factor list

factor_list = ['imbalance', 'z']



usage = "all"     # 'test' or 'all'，one day test or total data





########### Infrequently used config ##################

n1 = 30  # Remove the first n1 seconds of each opening and the last n2 seconds before closing
n2 = 10


divide_time_range = True  # Is the data only tested for a period of time after the opening?
open_minutes = 1000 # If testing only for a period of time after the opening, how many seconds after the opening are tested?

# I set this up to test if the factor had different results during the opening hours, as the market tends to be more active during those times.
# Later testing revealed little difference

extreme_value = False   # Whether to depolarize the factors