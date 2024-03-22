import geopandas as gpd
from rasterstats import zonal_stats

def zonal_statistics_to_csv(polygon_path, raster_path, statistics, output_name, index_col=None, drop_cols=None):
    
    gdf = gpd.read_file(polygon_path)

    if index_col != None:
        gdf.set_index(index_col, drop=True, inplace=True)

    stats = zonal_stats(gdf, raster_path, stats=statistics, all_touched=True)

    for key in statistics:
        gdf[key] = [stat[key] for stat in stats]

    if drop_cols != None:
        gdf.drop(columns=drop_cols, inplace=True)

    gdf.to_csv(output_name)