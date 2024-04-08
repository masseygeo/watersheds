# Cluster Analysis of Kentucky Watersheds and Comparison with Stream Hydrograph Data

***Matt Massey, Seun Adekunle, & Praneeth Bhatt***

Workflow in the following order...
1. [Data](./Data)
    1. [DataScraping_Spatial](./Data/DataScraping_Spatial.ipynb)
        1. *Download spatial data including digital elevation model (DEM) tiles, watershed boundaries, and political boundaries.*
    3. [DataScraping_StreamGauges](./Data/DataScraping_StreamGauges.ipynb)
        1. *Download stream gauge locations, then flood stage and discharge data for each gauge.*
    5. [PreProcessing_Spatial](./Data/PreProcessing_Spatial.ipynb)
        1. *Mosaic DEM tiles, exclude watersheds outside Kentucky, clip mosaic DEM to extent of selected watersheds, re-project to UTM coordinates, and save files and shapefiles.*
    7. [PreProcessing_StreamGauges](./Data/PreProcessing_StreamGauges.ipynb)
        1. *Get data type and time range information for each gauge, exclude gauges outside of area of interest, re-project to UTM coordinates, and save files and shapefiles.*
2. [TerrainFeatures](./TerrainFeatures)
    1. [TerrainFeatures](./TerrainFeatures/TerrainFeatures.ipynb)
        1. *Derive terrain features to characterize landscape in each watershed, and save each feature as a GeoTIFF in UTM coordinates.*
3. [WatershedClustering](./WatershedClustering)
    1. [ZonalStatistics](./WatershedClustering/ZonalStatistics.ipynb)
        1. *Aggregate statistics for all terrain feature by watershed, and save files.*
    3. Dimensionality Reduction and Clustering
4. [ElevatedStreamFlowEvents](./ElevatedStreamFlowEvents)
    1. [ELevatedStreamFlowEvents](./ElevatedStreamFlowEvents/ElevatedStreamFlowEvents.ipynb)
        1. *Plot stream gauge locations and watersheds, filter out stream gauges with insufficient data, plot hydrograph data for all suitable stream gauges in each watershed, identify elevated stream flow events based on threshold values, and plot watershed choropleth maps for event counts.*
    3. Correlation...
