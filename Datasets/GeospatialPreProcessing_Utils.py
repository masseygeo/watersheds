# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 14:09:40 2024

@author: mamass1
"""

import rasterio
from rasterio.merge import merge
import glob
import os


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
