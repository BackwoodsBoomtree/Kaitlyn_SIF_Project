
library(terra)

orig_dir      <- "/mnt/g/flash_drought/original"
output_dir    <- "/mnt/g/flash_drought/tif/0.20"
spatial_res   <- 0.20 # in degrees

agg  <- function(in_dir, out_dir, s_res) {
  
  start <- Sys.time() # Start clock for timing
  
  print(paste0("Start time is ", start))
  
  output_dir <- paste0(out_dir, "/")
  print(paste0("Output dir is: ", output_dir))
  
  template_raster <- rast(xmin = -180, xmax = 180, ymin = -90, ymax = 90,
                          ncols = 1800, nrows = 900, crs="+proj=longlat +datum=WGS84")
  
  correct_extent  <- ext(c(-125, -67, 25, 53)) # obtained from Metadata of the SMERGE
  
  if (!dir.exists(output_dir)) { # Create output dirs for each year
    dir.create(output_dir, recursive = TRUE)
  }
  
  file_list <- list.files(orig_dir, full.names = TRUE, pattern = "*.nc$")
  
  for (i in 1:length(file_list)) {
    
    print(paste0("Aggregating ", basename(file_list[i])))
    
    fd_nc        <- sds(file_list[i])
    fd_out_day   <- fd_nc[[1]]
    fd_out_len   <- fd_nc[[2]]
    ext(fd_out_day) <- correct_extent
    ext(fd_out_len) <- correct_extent
    fd_out_day      <- extend(fd_out_day, ext(c(-180, 180, -90, 90)))
    fd_out_len      <- extend(fd_out_len, ext(c(-180, 180, -90, 90)))
    
    fd_out_day <- resample(fd_out_day, template_raster, method = "near")
    fd_out_len <- resample(fd_out_len, template_raster, method = "near")

    out_name      <- substr(basename(file_list[i]), 1, 23)
    out_name_day  <- paste0(output_dir, "/", out_name, ".start.", toString(spatial_res), "deg.tif")
    out_name_len  <- paste0(output_dir, "/", out_name, ".length.", toString(spatial_res), "deg.tif")
    
    writeRaster(fd_out_day, filename = out_name_day, overwrite = TRUE, NAflag = -9999, datatype = 'INT4S')
    writeRaster(fd_out_len, filename = out_name_len, overwrite = TRUE, NAflag = -9999, datatype = 'INT4S')
    print(paste0("Saved files!"))
  }
}

agg(orig_dir, output_dir, spatial_res)