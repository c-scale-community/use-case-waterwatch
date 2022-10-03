# use-case-waterwatch

In this repository, the [Global Water Watch](https://www.globalwaterwatch.io/) algorithm is
translated to [OpenEO](https://openeo.org/) using their python API and user defined functions.

Global Water Watch is a project that uses Earth Observation data from many different sources
to obtain water availability for surface waterbodies globally through time. Tracking water
availability of surface waters globally can help detect droughts early.

Here, research notebooks are combined that test and visualize the algorithm, as well as code to
create an automatic process that extracts water availability from new Sentinel-2 data as soon as
it becomes available.

# Notebooks

## Run with Docker
build docker image:
`docker build . -t cgww`

run docker image:
`docker run -p 8888:8888 -v ~/.config:/home/jovyan/.config -v $(pwd):/home/jovyan/work cgww`
