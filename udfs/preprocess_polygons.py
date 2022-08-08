from typing import List, Optional

from openeo.udf import XarrayDataCube
import numpy as np
import xarray as xr

def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """
    Preprocess reservoir polygons to fill the polygon with nodata values.
    
    This function assumes a DataCube with Dimension 't' as an input.
    
    Args:
        cube (XarrayDataCube): datacube to apply the udf to.
        context (dict): key-value arguments.
    """

    # Load kwargs from context
    minimum_filled_fraction: Optional[float] = context.get("minimum_filled_fraction")
    if not minimum_filled_fraction:
        minimum_filled_fraction = 0.35
    
    quality_check_bands: Optional[List[str]] = context.get("quality_check_bands")
    if not quality_check_bands:
        quality_check_bands = ["green", "nir", "swir"]

    masked_value: Optional[int] = context.get("masked_value")
    if not masked_value:
        masked_value = -999999
    
    missing_value: Optional[int] = context.get("missing_value")
    if not missing_value:
        missing_value = -888888

    array: xr.DataArray = cube.get_array()
    # Need to get band index, as bands are not dims here
    indexes_used: List[int] = [bandname in quality_check_bands for bandname in array["bands"].values]
    check = array.isel(bands=indexes_used)
    masked = xr.where(check.sel(bands=quality_check_bands[0], drop=True) == masked_value, 1, 0)
    fraction_masked = masked.mean(dim=["x", "y"])
    print(fraction_masked)
    mean = 1 - np.isnan(check).mean(dim=["x", "y"])
    # Because we need all bands, use the most scarcely populated band as a filter criterion
    mean = mean.min(dim="bands")
    # Filter where the are too few observations.
    filtered: xr.DataArray = array.sel(t=mean.where(mean / (1 - fraction_masked) > minimum_filled_fraction, drop=True).t)
    # replace missing observations using missing value
    return XarrayDataCube(
        array=filtered
    )