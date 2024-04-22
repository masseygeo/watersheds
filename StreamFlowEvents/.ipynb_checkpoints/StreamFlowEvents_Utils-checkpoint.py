import glob
import pandas as pd
import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt


def get_timegap_indices(df, timegap_threshold):
    """Funciton to identify time gaps in timeseries and return start and end indices of gaps."""
    
    # get only non-null values (resample still keeps all data even if null and causes problems for diff)
    df_notna = df[df.notna().all(axis=1)]

    # calculate timedelta between observations
    diff = df_notna.index.diff()

    # get ending datetime indices for time gaps
    end_gap_idx = df_notna[diff > pd.Timedelta(timegap_threshold)].index

    # get list of locational positions (integers) for start indices of time gaps
    start_gap_idx = [df_notna.index.get_loc(end) - 1 for end in end_gap_idx]

    return end_gap_idx, start_gap_idx



def read_and_prepare_data(file_path, columns_to_drop, resample):
    """Read CSV file, drop specified columns, and set 'datetime' as index."""
    
    df = pd.read_csv(file_path, parse_dates=['datetime'], low_memory=False, delimiter=',')

    df = df.iloc[:, :6]

    df.drop(columns=df.columns[columns_to_drop], inplace=True)
    
    if df['datetime'].dtype != 'datetime64[ns]':
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M')   
    df.set_index('datetime', inplace=True)
    
    df.iloc[:,0] = pd.to_numeric(df.iloc[:,0], errors='coerce')

    
    df.rename(columns={df.columns[0]:f'mean_{resample}'}, inplace=True)
    
    df = df.resample(resample).mean()
    
    return df

def calculate_ci(df, window, min_periods, alpha):
    """Calculate moving average and margin of error envelope."""
    rolling = df.rolling(window, min_periods=min_periods)
    ma = rolling.mean().values.squeeze()
    std = rolling.std().values.squeeze()
    count = rolling.count().values.squeeze()
    degrees_freedom = np.maximum(count-1, 0)
    t_critical = np.where((count>1), t.ppf(1 - alpha/2, degrees_freedom), np.nan)
    mask = (~np.isnan(t_critical)) & (~np.isnan(std)) & (count>0)
    moe = np.where(mask, t_critical * std / np.sqrt(count), np.nan)
    df[f'ma_{window}'] = ma
    label = f'moe{int((1-alpha) * 100)}'
    df[label] = moe
    upperci = ma + moe
    df[f'{label}_bool'] = df.iloc[:,0] > upperci
    return df

def calculate_percentile(df, window, min_periods, percentile):
    rolling = df.iloc[:,0].rolling(window, min_periods=min_periods)
    q = percentile/100
    percentile_threshold = rolling.quantile(q=q).values.squeeze()
    label=f'percentile{percentile}'
    df[label] = percentile_threshold
    df[f'{label}_bool'] = df.iloc[:,0] > df[label]
    return df

def calculate_iqr_outlier(df, window, min_periods):
    rolling = df.iloc[:,0].rolling(window, min_periods=min_periods)
    q3 = rolling.quantile(q=0.75).values.squeeze()
    q1 = rolling.quantile(q=0.25).values.squeeze()
    iqr_outlier = (q3 - q1) * 1.5
    df['iqr_outlier'] = q3 + iqr_outlier
    df['iqr_outlier_bool'] = df.iloc[:,0] > df['iqr_outlier']
    return df

def process_gauge_data(gauge, data_type, columns_to_drop=[0,1,3,5], resample='1D', window='90D', min_periods='30', alpha=0.05):
    """Process gauge data based on type ('gh' or 'sf')."""
    if data_type == 'gauge height':
        file_path = glob.glob(f'../Data/stream_gauges/gauge_height/{gauge}*.csv')[0]
    else:
        file_path = glob.glob(f'../Data/stream_gauges/streamflow/{gauge}*.csv')[0]
    df = read_and_prepare_data(file_path, columns_to_drop, resample)
    df = calculate_ci(df, window, min_periods, alpha)
    df = calculate_percentile(df, window, min_periods, 90)
    df = calculate_percentile(df, window, min_periods, 99)
    # df = calculate_iqr_outlier(df, window, min_periods)
    return df


def create_subplot_axes(nrows):
    """Dynamically create subplot axes based on the number of rows."""
    fig, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True, figsize=(7, 4*nrows))
    # if nrows == 1:
    #     # axes = [axes]  # Ensure axes is always a list for consistency
    #     axes = np.array(axes).reshape(-1)
    # axes = np.array(axes).reshape(-1)
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


def stream_gauge_minimum_days(df, datetime_columns, indicator_columns, minimum_days_range):
    for dt, ind in zip(datetime_columns, indicator_columns):
        min_dt_mask = df[dt].dt.days < minimum_days_range
        df.loc[min_dt_mask, ind] = 0
    return df


def gauge_data_minimum_measurments(series, window, min_measurements):
    counts = series.rolling(window).count()
    return counts.max().item() >= min_measurements