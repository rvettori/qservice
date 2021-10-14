test:
	pytest

clean:
	rm -rf build/ dist/

build:
	python setup.py sdist bdist_wheel

check:
	twine check dist/*

upload_test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload_prod:
	twine upload dist/*
