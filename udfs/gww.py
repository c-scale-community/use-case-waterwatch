from typing import Optional

from openeo.udf import XarrayDataCube
import numpy as np
import xarray as xr

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
    mndwi_band: Optional[str] = context.get("mndwi_band")
    if not mndwi_band:
        mndwi_band = "MNDWI"
    
    wo_band: Optional[str] = context.get("wo_band")
    if not wo_band:
        wo_band = "wo"

    array: xr.DataArray = cube.get_array()

    # Need to get indexes and map to names for the incoming DataArray
    array_dim_dict = {name: i for i, name in enumerate(array.dims)}
    print(array_dim_dict)
    # get the two datasets
    mndwi = array.sel(bands=mndwi_band)
    wo = array.sel(bands=wo_band)
    # Also get indexes once bands has been removed
    bandless_dim_dict = {name: i for i, name in enumerate(mndwi.dims)}
    print(f"timeless dim: {bandless_dim_dict}")
    t_axis = bandless_dim_dict["t"]
    bands_axis = array_dim_dict["bands"]

    isnan = np.isnan(mndwi).values
    masked_mndwi = np.ma.array(mndwi.values, mask=isnan, fill_value=np.NaN)
    masked_wo = np.ma.array(wo.values, mask=isnan, fill_value=np.NaN)
    slices = [slice(None)]*mndwi.ndim
    for i in range(masked_mndwi.shape[t_axis]):
        slices[t_axis] = i
        mndwi_slice = masked_mndwi[tuple(slices)]
        wo_slice = masked_wo[tuple(slices)]
        nanmask = isnan[tuple(slices)]
        
        edge_image = canny(mndwi_slice, sigma=0.7, low_threshold=0.5, high_threshold=1)
        dilated = dilation(edge_image, footprint=np.ones([3, 3]))
        dilated = np.ma.array(dilated, mask=nanmask, fill_value=np.NaN)
        mndwi_edge = np.ma.array(mndwi_slice, mask=np.logical_or(nanmask, ~dilated))
        flat = mndwi_edge[~mndwi_edge.mask]
        flat = flat[~np.isnan(flat)]
        th = threshold_otsu(flat, nbins=100)
        print(f"otsu threshold: {th}")
        water = mndwi_slice > th
        water = np.ma.array(water, mask=nanmask, fill_value=np.NaN)
        area = water.sum() * 10e2 #m2
        print(f"area: {area}")
        
        wo_edge = np.ma.array(wo_slice, mask=np.logical_or(nanmask, ~dilated), fill_value=np.NaN)
        wo_flat = wo_edge[~wo_edge.mask]
        wo_flat = wo_flat[~np.isnan(wo_flat)]
        p = np.median(wo_flat)
        
        water_fill_JRC = wo_slice > p
        water_fill_JRC = np.ma.array(water_fill_JRC, mask=nanmask, fill_value=np.NaN)
        nonwater = mndwi_slice < -0.15
        water_fill = np.logical_and(nonwater, water_fill_JRC)
        area_filled = water_fill.sum() * 10e2
        print(f"area filled: {area_filled}")
        filled_fraction = area_filled / area
        print(f"filled fraction: {filled_fraction}")
        total_water = water_fill + water
        print(f"total_water_area: {total_water.sum() * 10e2}")
        assert total_water.sum() * 10e2 == area_filled + area
        
        total_water = np.expand_dims(total_water, axis=t_axis)
        water_fill = np.expand_dims(water_fill, axis=t_axis)
        water = np.expand_dims(water, axis=t_axis)
        
        if i == 0:
            w = water
            wf = water_fill
            tw = total_water
        else:
            w = np.append(w, water, axis=t_axis)
            wf = np.append(wf, water_fill, axis=t_axis)
            tw = np.append(tw, total_water, axis=t_axis)

    da_w = xr.DataArray(data=w, coords=mndwi.coords, dims=mndwi.dims).assign_coords({"bands": "water"})
    da_wf = xr.DataArray(data=wf, coords=mndwi.coords, dims=mndwi.dims).assign_coords({"bands": "water_fill"})
    da_tw = xr.DataArray(data=tw, coords=mndwi.coords, dims=mndwi.dims).assign_coords({"bands": "total_water"})

    array = xr.concat([array, da_w, da_wf, da_tw], dim="bands")
    return XarrayDataCube(array)