from typing import Optional

from openeo.udf import XarrayDataCube
import numpy as np
from xarray import DataArray

from skimage.filters.thresholding import threshold_otsu
from skimage.feature import canny
from skimage.morphology import dilation

def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """
    Applies Ostu thresholding to the datacube.
    
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

    # TODO: vectorize over all t
    img = array.isel(t=0)

    can: DataArray = canny(img, sigma=0.7, low_threshold=0.5, high_threshold=1)
    thresh = threshold_otsu(img.values, nbins=100)

    dilated = dilation(can, footprint=np.ones([3, 3]))
    mndwi_edge = img.where(dilated)
    flat = mndwi_edge.values.ravel()
    flat = flat[~np.isnan(flat)]
    th = threshold_otsu(flat, 100)
    water = img > th
    area = water.isel(t=3).sum() * 10e2 #m2

    print(filtered.shape)
    return XarrayDataCube(
        array=filtered
    )