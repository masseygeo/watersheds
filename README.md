# Clustering Kentucky Watershed Landscapes And Comparison With Elevated Stream Flow Event Frequencies

***Matt Massey, Seun Adekunle, & Praneeth Bhatt***

Our approach and workflow was completed in the following order (see linked folders and notebooks for additional notes and documentation of implementations)...
1. [Data](./Data)
    1. [DataScraping_Spatial](./Data/DataScraping_Spatial.ipynb)
        1. *Download spatial data including digital elevation model (DEM) tiles, watershed boundaries, and political boundaries.*
    2. [DataScraping_StreamGauges](./Data/DataScraping_StreamGauges.ipynb)
        1. *Download stream gauge locations, then flood stage and discharge data for each gauge.*
    3. [PreProcessing_Spatial](./Data/PreProcessing_Spatial.ipynb)
        1. *Mosaic DEM tiles, exclude watersheds outside Kentucky, clip mosaic DEM to extent of selected watersheds, re-project to UTM coordinates, and save files and shapefiles.*
    4. [PreProcessing_StreamGauges](./Data/PreProcessing_StreamGauges.ipynb)
        1. *Get data type and time range information for each gauge, exclude gauges outside of area of interest, re-project to UTM coordinates, and save files and shapefiles.*
2. [TerrainFeatures](./TerrainFeatures)
    1. [TerrainFeatures](./TerrainFeatures/TerrainFeatures.ipynb)
        1. *Calculate terrain features in order to characterize the local landscape of each watershed in detail, and save each new feature as a GeoTIFF in UTM coordinates.*
3. [WatershedClustering](./WatershedClustering)
    1. [ZonalStatistics](./WatershedClustering/ZonalStatistics.ipynb)
        1. *Aggregate statistics of terrain features for each watershed, and save as .csv files.*
    2. [PCA]
        1. *Merge aggregated statistics .csv files by watershed ID into single dataframe, normalize each attribute, and reduce dimensionality using princiapl component analysis (PCA).*
    3. Clustering_KMeans
    4. Clustering_DBSCAN
    5. Clustering_HDBSCAN
4. [ElevatedStreamFlowEvents](./ElevatedStreamFlowEvents)
    1. [ELevatedStreamFlowEvents](./ElevatedStreamFlowEvents/ElevatedStreamFlowEvents.ipynb)
        1. *Plot stream gauge locations and watersheds, filter out stream gauges with insufficient data, plot hydrograph data for all suitable stream gauges in each watershed, identify elevated stream flow events based on threshold values, and plot watershed choropleth maps for event counts.*
    3. Correlation...
