DOCKER_IMAGE_NAME= my-python-app

install:
	pip install -r src/requirements.txt

install_test:
	pip install -r tests/requirements.txt

test:
	pytest

lint:
	black .
	pylama .

docker_build:
	sudo docker build -t $(DOCKER_IMAGE_NAME) .

docker_run:
	sudo docker run $(DOCKER_IMAGE_NAME) python main.py value1 value2 value3