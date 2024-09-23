## About
This project was written during my previous internship to test high frequency alphas. 
Putting it here partly as an archive and partly to give some possible help to others. This framework may be difficult to replicate unless you have order book data from the Shanghai Futures Exchange like I do.

Note that this framework is copied from my framework for ss(stainless steels) at SHFE. Some modifications may be needed for other species, such as the closing time of the night market, etc.

## Structure:
### factors.py: 
The specific implementation logic for the factor is here. Calling get_alpha from that file returns the dataframe of the factor value.
### Data_process.py: 
Cleaning of data
### Performance_Analysis.py: 
Calculate, output factor performance. Mainly include IC, correlation, quantile y-mean histogram, distribution plot.
### config.py: 
Configure some variable parameters
### main_demo.py: 
The main script, calls the remaining four files.

## Data:
The input data is orderbook data (i.e. snapshot data), which mainly contains Bidprice1-5, BidVolume1-5, and the corresponding Ask data.

I have this data for several different species for over 9 months, but I've only included the csv data for a particular day here. 
This is because this type of data is usually expensive and I don't want to give away company secrets here. 
The y_pos markers in the data are pre-labeled to represent the rise and fall over the next 3-5 seconds. This is also the label that needs to be predicted.


## Alpha:
I only provide two sample alphas in factors.py. Of course I will not put all my alphas on github! 😎 The alphas are to predict the movement of the next 3-5 seconds. So this is a time-series factor, not a cross-sectional stock picker common in stocks.
The main measure of the predictive effectiveness of the factors is the IC, which is the correlation between the factor series and the y series.

(Note: Here we simply consider the predictive power, or corr, for the time being. Other factors such as kurtosis and skewness do not need to be measured for the time being, but may be considered in subsequent modeling or risk control sessions)


