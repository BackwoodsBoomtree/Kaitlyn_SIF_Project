# Kaitlyn SIF Project

The scripts here are for Kaitlyn's SIF project.

## Scripts

* fix_extent_fd.py - This script corrects the extent and assigns wgs84 crs to Jordan's original flash drought data. The aggregation code below is outdated as the workflow is to now grid TROPOMI to 0.125-deg to match the flash drought maps.

* Aggregate_Flash_Drought.R - This script aggregates Jordan Christian's v02 flash drought maps to 0.20 to match TROPOMI. Outputs a TIF for start date and length of flash drought. Uses neariest neighbor resampling (you can think of the start day and length as a classification rather than a continuous variable).
