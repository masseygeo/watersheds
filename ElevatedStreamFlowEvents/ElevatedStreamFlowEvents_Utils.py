import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt


def read_and_prepare_data(file_path, columns_to_drop):
    """Read CSV file, drop specified columns, and set 'datetime' as index."""
    df = pd.read_csv(file_path, parse_dates=['datetime'])
    df.drop(columns=df.columns[columns_to_drop], inplace=True)
    df.set_index('datetime', inplace=True)
    return df

def calculate_ci(df, window, alpha):
    """Calculate moving average and margin of error envelope."""
    rolling = df.rolling(window, min_periods=30)
    ma = rolling.mean().values.squeeze()
    std = rolling.std().values.squeeze()
    count = rolling.count().values.squeeze()
    degrees_freedom = np.maximum(count-1, 0)
    t_critical = np.where((count>1), t.ppf(1 - 0.05/2, degrees_freedom), np.nan)
    mask = (~np.isnan(t_critical)) & (~np.isnan(std)) & (count>0)
    moe = np.where(mask, t_critical * std / np.sqrt(count), np.nan)
    df[f'ma_{window}'] = ma
    label = f'moe{int((1-alpha) * 100)}'
    df[label] = moe
    upperci = ma + moe
    df[f'{label}_bool'] = df.iloc[:,0] > upperci
    return df

def calculate_percentile(df, window, percentile):
    rolling = df.iloc[:,0].rolling(window, min_periods=30)
    q = percentile/100
    percentile_threshold = rolling.quantile(q=q).values.squeeze()
    label=f'percentile{percentile}'
    df[label] = percentile_threshold
    df[f'{label}_bool'] = df.iloc[:,0] > df[label]
    return df

def calculate_iqr_outlier(df, window):
    rolling = df.iloc[:,0].rolling(window, min_periods=30)
    q3 = rolling.quantile(q=0.75).values.squeeze()
    q1 = rolling.quantile(q=0.25).values.squeeze()
    iqr_outlier = (q3 - q1) * 1.5
    df['iqr_outlier'] = q3 + iqr_outlier
    df['iqr_outlier_bool'] = df.iloc[:,0] > df['iqr_outlier']
    return df

def process_gauge_data(gauge, data_type, columns_to_drop=[0,1,3,5], resample='1D', window='90D', alpha=0.05, percentile=95):
    """Process gauge data based on type ('gh' or 'sf')."""
    if data_type == 'gauge height':
        file_path = glob.glob(f'../Data/stream_gauges/gauge_height/{gauge}*.csv')[0]
    else:
        file_path = glob.glob(f'../Data/stream_gauges/streamflow/{gauge}*.csv')[0]
    df = read_and_prepare_data(file_path, columns_to_drop)
    df.rename(columns={df.columns[0]:f'mean_{resample}'}, inplace=True)
    df = df.resample(resample).mean()
    df = calculate_ci(df, window, alpha)
    df = calculate_percentile(df, window, percentile)
    df = calculate_iqr_outlier(df, window)
    return df


def create_subplot_axes(nrows):
    """Dynamically create subplot axes based on the number of rows."""
    fig, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True, figsize=(7, 4*nrows))
    if nrows == 1:
        axes = [axes]  # Ensure axes is always a list for consistency
    return fig, axes


def get_frequencies(df, resample='1YE', data_type='gauge height'):
    count_columns = [col for col in df.columns.values if 'bool' in col]
    df_counts = df[count_columns].resample(resample).sum()
    df_counts = df_counts.iloc[1:]
    if data_type == 'gauge height':
        df_counts.columns = [f'{col}_gh' for col in df_counts.columns]
    else:
        df_counts.columns = [f'{col}_sf' for col in df_counts.columns]
    return df_counts.mean()


def assign_frequencies(df, series, gauge_id):
    for index, row in series.items():
        if index not in df.columns:
            df[index] = np.nan
        df.loc[df['site_no'] == gauge_id, index] = row