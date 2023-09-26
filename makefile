install:
	pip install -r src/requirements.txt

install_test:
	pip install -r tests/requirements.txt

test:
	pytest

lint:
	find . -name "*.py" | xargs black