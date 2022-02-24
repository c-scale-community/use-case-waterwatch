# use-case-waterwatch

## Run with Docker
build docker image:
`docker build . -t cgww`

run docker image:
`docker run -p 8888:8888  -v ~/.config/gcloud:/home/jovyan/.config/gcloud -v $(pwd):/home/jovyan/work cgww`
