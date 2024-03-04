#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 11:09:55 2024

@author: Matthew
"""

url_gageheight = r'https://nwis.waterdata.usgs.gov/ky/nwis/uv/?index_pmcode_00065=1&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=site_no&column_name=station_nm&column_name=dec_lat_va&column_name=dec_long_va&column_name=alt_va&column_name=huc_cd&column_name=basin_cd&column_name=rt_bol&range_selection=date_range&begin_date={begin_date}&end_date={end_date}&date_format=YYYY-MM-DD&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection'

url_streamflow = r'https://nwis.waterdata.usgs.gov/ky/nwis/uv/?index_pmcode_00060=1&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=site_no&column_name=station_nm&column_name=dec_lat_va&column_name=dec_long_va&column_name=alt_va&column_name=huc_cd&column_name=basin_cd&column_name=rt_bol&range_selection=date_range&begin_date={begin_date}&end_date={end_date}&date_format=YYYY-MM-DD&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection'


def get_usgs_gage_locations(dir, data='gage height', begin_date='1950-10-01', end_date=datetime.today().strftime('%Y-%m-%d')):

    if data == 'gage height':

        data_path = os.path.join(
            dir, f'gage_height_{begin_date}_{end_date}.csv')
        metadata_path = os.path.join(
            dir, f'gage_height_{begin_date}_{end_date}_metadata.txt')

    elif data == 'streamflow':

        data_path = os.path.join(
            dir, f'streamflow_{begin_date}_{end_date}.csv')
        metadata_path = os.path.join(
            dir, f'streamflow_{begin_date}_{end_date}_metadata.txt')

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

            # Check if the line is a comment
            if line.startswith('#'):

                # Write the comment line to the comments file
                textfile.write(line + '\n')

    return data_path
