from typing import Optional

from openeo.udf import XarrayDataCube
import numpy as np
from xarray import DataArray

def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """
    Filter the datacube based on the quality band and the quantile of the band values.
    
    This function assumes a DataCube with Dimension 't' as an input.
    
    Args:
        cube (XarrayDataCube): datacube to apply the udf to.
        context (dict): key-value arguments.
    """

    # Load kwargs from context
    cutoff_percentile: Optional[float] = context.get("cutoff_percentile")
    if not cutoff_percentile:
        cutoff_percentile = 35
    cutoff_percentile = cutoff_percentile / 100.

    score_percentile: Optional[float] = context.get("score_percentile")
    if not score_percentile:
        score_percentile = 75.
    score_percentile = score_percentile / 100.

    quality_band: Optional[str] = context.get("quality_band")
    if not quality_band:
        quality_band = "cloudp"

    array: DataArray = cube.get_array()
    # Need to get band index, as bands are not dims here
    index = np.where(array["bands"].values == quality_band)[0][0]
    score: DataArray = array.isel(bands=index).quantile([score_percentile], dim=["x", "y"])
    filtered: DataArray = array.sel(t=score.where(score / np.max(score) < cutoff_percentile, drop=True).t)
    print(filtered.shape)
    return XarrayDataCube(
        array=filtered
    )
