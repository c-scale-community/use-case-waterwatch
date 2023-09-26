# use-case-waterwatch

[![Binder](https://replay.notebooks.egi.eu/badge_logo.svg)](https://replay.notebooks.egi.eu/v2/gh/c-scale-community/use-case-waterwatch/HEAD?labpath=openeo_waterwatch.ipynb)

In this repository, the [Global Water Watch](https://www.globalwaterwatch.io/) algorithm is
translated to [OpenEO](https://openeo.org/) using their python API and user defined functions.

Global Water Watch is a project that uses Earth Observation data from many different sources
to obtain water availability for surface waterbodies globally through time. Tracking water
availability of surface waters globally can help detect droughts early.

Here, research notebooks are combined that test and visualize the algorithm, as well as code to
create an automatic process that extracts water availability from new Sentinel-2 data as soon as
it becomes available.

# Notebooks

## Local Docker image

Build docker image:


```bash
docker build -t cgww docker
```

Run docker image:

```bash
docker run -p 8888:8888 -v ~/.config:/home/jovyan/.config -v $(pwd):/home/jovyan/work cgww
```

## Binder

You can also run the WaterWatch notebook using
[EGI Replay](https://replay.notebooks.egi.eu/v2/gh/c-scale-community/use-case-waterwatch/HEAD?labpath=openeo_waterwatch.ipynb).

Pre-requisites:
* Create an [EGI Account](https://docs.egi.eu/users/aai/check-in/signup/)
* Enroll the `vo.notebooks.egi.eu` Virtual Organisation following this link:
  https://aai.egi.eu/registry/co_petitions/start/coef:111
