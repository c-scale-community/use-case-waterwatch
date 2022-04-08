import os
from pathlib import Path
from typing import List, Optional, Union

import fiona
from google.cloud.storage import Blob, Bucket, Client
from shapely.geometry import MultiPolygon, Polygon

# Otherwise proj bugs out
os.environ["PROJ_LIB"] = "/opt/conda/share/proj"


class Reservoir:
    def __init__(
        self,
        fid: int,
        geometry: Union[MultiPolygon, Polygon],
        source_name: str,
        source_id: Optional[str] = None,
        name: Optional[str] = None,
        name_en: Optional[str] = None,
        grand_id: int = None
    ) -> "Reservoir":
        self._fid = fid
        self._source_name = source_name
        self._source_id = source_id
        self._geometry = geometry
        self._name = name,
        self._name_en = name_en,
        self._grand_id = grand_id

    @property
    def geometry(self) -> Union[MultiPolygon, Polygon]:
        return self._geometry
    
    def fid(self) -> int:
        return self._fid
    
    @classmethod
    def from_gcp(
        cls: "Reservoir",
        out_dir: Path,
        gcp_project: str = "global-water-watch",
        gcp_bucket: str = "global-water-watch"
    ) -> List["Reservoir"]:
        """
        downloads shape files from gcp bucket source and creates a list of available Reservoirs.

        args:
            out_dir (Path): directory where downloads are gathered.
            gcp_project (str): Google Cloud Platform Project.
            gcp_bucket (str): Google Cloud Platform Bucket.
        """
        os.environ["GCLOUD_PROJECT"] = gcp_project

        client: Client = Client()
        bucket: Bucket = Bucket(client, name=gcp_bucket, user_project=gcp_project)

        blob: Blob = client.list_blobs(bucket, prefix="shp/reservoirs-v1.0")
        for b in blob:
            b.download_to_filename(out_dir / b.name.split("/")[-1])
            
        shapes = fiona.open(out_dir / "reservoirs-v1.0.shp")

        def process_shapes(shape: dict):
            s_type: str = shape["geometry"]["type"]
            coords: List = shape["geometry"]["coordinates"]
            if s_type == "MultiPolygon":
                geometry: MultiPolygon = MultiPolygon([Polygon(c[0]) for c in coords])
            elif s_type == "Polygon":
                geometry: Polygon = Polygon(coords[0])
            
            properties: dict = shape["properties"]
            return cls(
                fid=properties["fid"],
                source_name=properties["source_nam"],
                geometry=geometry,
                source_id=properties["source_id"],
                name=properties["name"],
                name_en=properties["name_en"],
                grand_id=properties["grand_id"]
            )

        return list(map(process_shapes, iter(shapes)))