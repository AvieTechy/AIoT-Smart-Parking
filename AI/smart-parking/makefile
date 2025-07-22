IMAGE_NAME = smart-parking-api
CONTAINER_NAME = smart-parking-api
PORT = 8000

.PHONY: build run stop

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run --rm -d -p $(PORT):8000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME)
