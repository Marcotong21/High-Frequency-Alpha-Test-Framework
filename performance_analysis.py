import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
import os
import numpy as np
import seaborn as sns



def IC_quantile(factor_values):
    """
        Calculate the IC and head and tail means of each factor and output them
    :param factor_values: a dataframe containing the values of each factor along with the y-values
    :return: outputs the IC for each factor and the corr of the factors to result
    """

    if len(factor_values) < 200000:  # if it's test data
        factor_dir = 'result_test/test_performance.csv'
    else:                            # it's total data
        factor_dir = 'result/total performance.csv'

    results = pd.DataFrame(columns=['IC', 'Top 1% Mean y', 'Bottom 1% Mean y', 'bottom_win_rate', 'top_win_rate'])
    # Calculate the IC
    # Calculate the correlation matrix for the entire DataFram
    correlation_matrix = factor_values.corr()
    # Extracting the corr associated with column 'y' (removing 'y' from itself) which is the IC value
    ic_values = correlation_matrix['y'].drop('y')
    # After removing column 'y' and row 'y' from the correlation matrix, the matrix remain is the corr matrix
    factor_correlation_matrix = correlation_matrix.drop('y', axis=0).drop('y', axis=1)

    # output corr.txt
    corr_matrix_path = os.path.join('result', 'Correlation_matrix.txt')
    with open(corr_matrix_path, 'w') as file:
        factor_correlation_matrix.to_string(file)
    # Heat map of output abs(corr)
    plt.figure(figsize=(10, 8))
    factor_correlation_matrix = np.abs(factor_correlation_matrix)
    # Heatmap using seaborn's heatmap function
    sns.heatmap(factor_correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, center=0)
    plt.title('Correlation Matrix')
    heatmap_path = os.path.join('result', 'Correlation_matrix(abs).png')
    plt.savefig(heatmap_path)

    # Calculate the head and tail 1% quantile for each factor
    # Get the values of the factors except y
    factor_columns = factor_values.columns.difference(['y'])
    for factor in factor_columns:
        # Calculate the 1% and 99% quantiles
        q_low = factor_values[factor].quantile(0.01)
        q_high = factor_values[factor].quantile(0.99)
        # Filter out the 'y' values that correspond to these two quantiles
        top_1_percent_y = factor_values[factor_values[factor] >= q_high]['y']
        bottom_1_percent_y = factor_values[factor_values[factor] <= q_low]['y']
        # calculate quantile mean
        top_mean = top_1_percent_y.mean()
        bottom_mean = bottom_1_percent_y.mean()
        # Calculate the percentage greater than zero (win rate)
        # sign of if correlation(IC) is positive or negative
        sign = 1 if ic_values[factor]>0 else -1
        # top_win_rate = top_1_percent_y[sign * top_1_percent_y > 0].count() / len(top_1_percent_y)
        # bottom_win_rate = bottom_1_percent_y[sign * bottom_1_percent_y < 0].count() / len(bottom_1_percent_y)
        top_win_rate = top_1_percent_y[sign * top_1_percent_y > 0].count() / top_1_percent_y[sign * top_1_percent_y != 0].count()
        bottom_win_rate = bottom_1_percent_y[sign * bottom_1_percent_y < 0].count() / bottom_1_percent_y[sign * bottom_1_percent_y != 0].count()

        results = results.append({'Factor': factor,
                                  'IC':ic_values.loc[factor],
                                  'Top 1% Mean y': top_mean,
                                  'Bottom 1% Mean y': bottom_mean,
                                  'top_win_rate': top_win_rate,
                                  'bottom_win_rate': bottom_win_rate
                                  }, ignore_index=True)
    results = results.set_index('Factor')
    results = results.reindex(results['IC'].abs().sort_values(ascending=False).index)
    results.to_csv(factor_dir)
    return


def output(data):
    """
        quantile histogram and statistical distribution analysis, graphical output in results folder
    :param data: also known as factor_values, same function as above.
    :return: output the charts to result.
    """
    # Get all columns except 'y'
    factor_columns = data.columns.difference(['y'])

    for factor in factor_columns:
        # Create a separate folder for each factor to hold plots
        if len(data) < 200000:   # plot iff it's total data
            continue
        else:
            factor_dir = os.path.join('result', factor)

        if not os.path.exists(factor_dir):
            os.makedirs(factor_dir)

        # # 1.ACF
        # fig, ax = plt.subplots(figsize=(10, 4))
        # plot_acf(data[factor].iloc[:150000], ax=ax, lags=20, title=f'Autocorrelation for {factor}')
        # acf_path = os.path.join(factor_dir, f'{factor}-ACF.png')
        # plt.savefig(acf_path)
        # plt.close(fig)

        # Calculate bins and counts for histograms
        counts, bin_edges = np.histogram(data[factor], bins=30, density=True)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        # 2. Plotting line graphs for histograms
        plt.figure(figsize=(10, 6))
        plt.plot(bin_centers, counts, linestyle='-', marker='o', color='b')
        plt.title(f'Probability Density Function - {factor}')
        plt.xlabel('Factor Value')
        plt.ylabel('Density')
        plt.grid(True)
        distribution_path = os.path.join(factor_dir, f'{factor}-distribution.png')
        plt.savefig(distribution_path)
        plt.close()

        # 3. Generate y-means for each quantile
        fig, ax = plt.subplots(figsize=(10, 6))
        bins = np.arange(0, 1.01, 0.01)  # Sub-boxes for generating histograms
        bin_means = []
        # Get the y-mean for each quartile
        for i in range(len(bins) - 1):
            left = bins[i]
            right = bins[i + 1]
            # todo: is it really better to set it to null, or is it better to juxtapose the values?
            y_values = data[(data[factor] >= data[factor].quantile(left)) & (data[factor] <= data[factor].quantile(right))]['y']
            mean_y = y_values.mean()
            bin_means.append(mean_y)
        ax.bar(bins[:-1], bin_means, width=0.01)
        ax.set_xticks(np.arange(0, 1.01, 0.1))
        ax.set_xlabel('Quantile Range')
        ax.set_ylabel('Mean y')
        ax.set_title(f'Mean y by {factor} Quantile Ranges')
        hist_path = os.path.join(factor_dir, f'{factor}_quantile_histogram.png')
        fig.savefig(hist_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    return


def orthogonal(factor1, factor2):    # didn't used here
    """
        Orthogonalizes factor1 using factor2 as a reference. Returns orthogonalized factor1
    :param factor1: The factor to be orthogonalized.
    :param factor2: the reference factor
    :return.
    """
    # Calculate the variance of the reference factor
    var_factor2 = np.var(factor2)
    # Calculate the covariance of factor1 with the reference factor
    cov_factor1_factor2 = np.cov(factor1, factor2)[0, 1]
    # Calculate factor1 after orthogonalization
    orthogonal_factor1 = factor1 - (cov_factor1_factor2 / var_factor2) * factor2
    return orthogonal_factor1




