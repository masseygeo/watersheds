#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 11:09:55 2024

@author: Matthew
"""


import requests
from datetime import datetime
import csv
import os
import rasterio
from rasterio.merge import merge
import glob


def get_stream_gauge_locations(save_dir, data='gage height', state='ky', begin_date='1950-10-01', end_date=datetime.today().strftime('%Y-%m-%d')):

    if data == 'gage height':

        url = f"https://nwis.waterdata.usgs.gov/{state}/nwis/uv/?index_pmcode_00065=1&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=site_no&column_name=station_nm&column_name=dec_lat_va&column_name=dec_long_va&column_name=alt_va&column_name=huc_cd&column_name=basin_cd&column_name=rt_bol&range_selection=date_range&begin_date={begin_date}&end_date={end_date}&date_format=YYYY-MM-DD&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection"

        data_path = os.path.join(
            save_dir, f'gage_height_{begin_date}_{end_date}.csv')

        metadata_path = os.path.join(
            save_dir, f'gage_height_{begin_date}_{end_date}_metadata.txt')

    elif data == 'streamflow':

        url = f"https://nwis.waterdata.usgs.gov/{state}/nwis/uv/?index_pmcode_00060=1&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=site_no&column_name=station_nm&column_name=dec_lat_va&column_name=dec_long_va&column_name=alt_va&column_name=huc_cd&column_name=basin_cd&column_name=rt_bol&range_selection=date_range&begin_date={begin_date}&end_date={end_date}&date_format=YYYY-MM-DD&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection"

        data_path = os.path.join(
            save_dir, f'streamflow_{begin_date}_{end_date}.csv')

        metadata_path = os.path.join(
            save_dir, f'streamflow_{begin_date}_{end_date}_metadata.txt')

    response = requests.get(url)
    text_data = response.text
    lines = text_data.splitlines()

    with open(data_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for line in lines:
            if not line.startswith('#') and line.strip():
                data = line.split('\t')
                csvwriter.writerow(data)

    with open(metadata_path, 'w') as textfile:
        for line in lines:
            if line.startswith('#'):
                textfile.write(line + '\n')

    return data_path


def get_stream_gage_data(gage_id, save_dir, data='gage height', begin_date='1950-10-01', end_date=datetime.today().strftime('%Y-%m-%d')):

    # handle missing directory from save_dir parameter
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # get data type from data parameter
    if data == 'gage height':
        parameter_id = '00065'
    
    if data == 'streamflow':
        parameter_id = '00060'

    # format url using gage_id, parameter_id, begin_date, and end_date parameters
    url = f"https://waterservices.usgs.gov/nwis/iv/?sites={gage_id}&parameterCd={parameter_id}&startDT={begin_date}T00:00:00.176-05:00&endDT={end_date}T00:00:00.176-05:00&siteStatus=all&format=rdb"

    # create path to save data as .csv file
    data_path = os.path.join(save_dir, f"{gage_id}_{data.replace(' ','')}_{begin_date}_{end_date}.csv")

    # submit request for response using url
    response = requests.get(url)

    # if response is valid then proceed with data scraping
    if response.status_code == 200:

        # convert response to text
        text_data = response.text

        # split text into lines
        lines = text_data.splitlines()

        # initialize counter for non-comment line numbers
        non_comment_line_counter = 0

        # write data from response to file (in-memory)
        with open(data_path, 'w', newline='') as csvfile:

            # initialize csv writer from text
            csvwriter = csv.writer(csvfile)

            # iterate through lines from response/text
            for line in lines:

                # skip comment lines starting with # or blank lines
                if line.startswith('#') or not line.strip():
                    continue

                # if line is not a comment or blank, increase the line number counter
                non_comment_line_counter += 1

                # first line is header info, which is kept; second line is meaningless, which is skipped here
                if non_comment_line_counter == 2:
                    continue

                # split lines into new lines using a tab
                data = line.split('\t')

                # write line to csv file
                csvwriter.writerow(data)
    


def mosaic_dem_tiles(input_dir, output_path):
    """
    Function to merge multiple geotiff files and save as new, single geotiff.

    Parameters
    ----------
    input_dir : list
        Path of directory containing input geotiff files.
    output_path : string
        Path for new geotiff mosaic output file.

    Returns
    -------
    None.

    """
    tiles_paths = glob.glob(os.path.join(input_dir, '*.tif'))

    tiles_datasets = []

    for tile in tiles_paths:
        dem = rasterio.open(tile)
        tiles_datasets.append(dem)

    mosaic, transform = merge(tiles_datasets)

    mosaic_metadata = tiles_datasets[0].meta.copy()

    mosaic_metadata.update({'driver': 'GTiff',
                            'height': mosaic.shape[1],
                            'width': mosaic.shape[2],
                            'transform': transform,
                            'count': mosaic.shape[0]})   # number of bands

    with rasterio.open(output_path, 'w', **mosaic_metadata) as output_raster:
        output_raster.write(mosaic)

    for dem in tiles_datasets:
        dem.close()