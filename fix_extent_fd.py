
import os
from netCDF4 import Dataset
from datetime import datetime
from osgeo import gdal
import numpy as np

# Input arguments 
in_path   = '/mnt/g/flash_drought/original'
out_path  = '/mnt/g/flash_drought/fix_extent'

def fix_geo(in_path, out_path):
    
    in_files  = sorted([os.path.join(in_path, l) for l in os.listdir(in_path) if l.endswith('.nc')])
    out_files = [x.replace(in_path, out_path).replace('.nc', '.wgs84.nc') for x in in_files]
    
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        
    extent = [-125, -67, 25, 53]
    
    for i in range(len(in_files)):
            
        # Get variables from nc input file
        fd_start = gdal.Open("NETCDF:{0}:{1}".format(in_files[i], 'fd_start_date'))
        fd_len   = gdal.Open("NETCDF:{0}:{1}".format(in_files[i], 'fd_length'))
        
        # Transform to array and set the existing fills to -9999 to flag as na
        # Note that no data value is very large in input data
        fd_start                               = fd_start.ReadAsArray()
        fd_len                                 = fd_len.ReadAsArray()
        fd_start[fd_start == np.max(fd_start)] = -9999
        fd_len[fd_len == np.max(fd_len)]       = -9999
    
        # Create NetCDF file    
        nco = Dataset(out_files[i], 'w', format = "NETCDF4")
        
        # Meta-data  
        nco.LongName        = "Flash Drought CONUS"
        nco.ShortName       = "Flash Drought CONUS"
        nco.GranuleID       = os.path.basename(out_files[i])
        nco.VersionID       = '1.0'
        nco.Format          = 'NetCDF4'
        nco.Conventions     = 'CF-1.9'
        nco.ProcessingLevel = 'Level 3'
        nco.Source          = 'Dr. Jordan Christian'
        nco.ProcessingCenter     = 'University of Oklahoma College of Atmospheric and Geographic Sciences'
        nco.ContactPersonName    = 'Jordan, Christian'
        nco.ContactPersonRole    = 'Post Doctoral Researcher'
        nco.ContactPersonEmail   = 'jchristian@ou.edu'
        nco.ContactPersonAddress = '120 David L. Boren Blvd., Norman, Oklahoma 73072, USA'
        nco.SouthernBoundingCoordinate = str(extent[2])
        nco.NorthernBoundingCoordinate = str(extent[3])
        nco.WesternBoundingCoordinate  = str(extent[0])
        nco.EasternBoundingCoordinate  = str(extent[1])
        nco.LatitudeResolution  = '0.125'
        nco.LongitudeResolution = '0.125'
        nco.ProductionDateTime  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nco.comment     = ('This data as been extended to the global scale and assigned a crs using the original data by Russell Doughty.')

        # These need to be coordinates of the center of the gridcells
        lon_list   = np.arange(extent[0] + (0.125 / 2), extent[1], 0.125)
        lat_list   = np.flip(np.arange(extent[2] + (0.125 / 2), extent[3], 0.125))
        
        # Create dimensions, variables and attributes
        nco.createDimension('lon', len(lon_list))
        nco.createDimension('lat', len(lat_list))
        
        # Lon
        lon               = nco.createVariable('lon', 'f4', ('lon',))
        lon.standard_name = 'longitude'
        lon.units         = 'degrees_east'
        
        # Lat
        lat               = nco.createVariable('lat', 'f4', ('lat',))
        lat.standard_name = 'latitude'
        lat.units         = 'degrees_north'

        # CRS - These values pulled from gdalinfo after converting GeoTiffs to WGS84
        crs                             = nco.createVariable('WGS84', 'i4')
        crs.long_name                   = 'World Geodetic System 1984 (WGS84)'
        crs.grid_mapping_name           = 'latitude_longitude'
        crs.longitude_of_prime_meridian = 0.0
        crs.semi_major_axis             = 6378137.0
        crs.inverse_flattening          = 298.257223563
        crs.spatial_ref                 = 'GEOGCRS["WGS 84", DATUM["World Geodetic System 1984", ELLIPSOID["WGS 84",6378137,298.257223563, LENGTHUNIT["metre",1]]], PRIMEM["Greenwich",0, ANGLEUNIT["degree",0.0174532925199433]], CS[ellipsoidal,2], AXIS["geodetic latitude (Lat)",north, ORDER[1], ANGLEUNIT["degree",0.0174532925199433]], AXIS["geodetic longitude (Lon)",east, ORDER[2], ANGLEUNIT["degree",0.0174532925199433]], ID["EPSG",4326]]'
        
        # Variable
        var_start = nco.createVariable('fd_start_date', 'i4', ('lat', 'lon'), zlib = True, fill_value = -9999)
        var_start.long_name    = "Start Date for Flash Drought (DOY)"
        var_start.units        = 'doy'
        var_start.grid_mapping = 'WGS84'
        var_start.set_auto_maskandscale(False)
        
        # Variable
        var_len = nco.createVariable('fd_length', 'i4', ('lat', 'lon'), zlib = True, fill_value = -9999)
        var_len.long_name    = "Length of the Flash Drought (pentads)"
        var_len.units        = 'pentads'
        var_len.grid_mapping = 'WGS84'
        var_len.set_auto_maskandscale(False)

        # Write lon,lat
        lon[:] = lon_list
        lat[:] = lat_list

        # Write data
        var_start[:, :] = fd_start
        var_len[:, :]   = fd_len
        nco.close()
        print('I have created the file: %s\n' % os.path.basename(out_files[i]))
        
fix_geo(in_path, out_path)