.PHONY: all virtualenv install test local upload

SHELL := /usr/bin/env bash

all: virtualenv install

virtualenv:
	@if [ ! -d ".venv" ]; then \
		python3 -m pip install virtualenv --user; \
		python3 -m virtualenv .venv; \
	fi

install: virtualenv
	@( \
		source .venv/bin/activate; \
		python -m pip install -r requirements.txt; \
		python -m pip install -r requirements-dev.txt; \
	)

test: virtualenv
	@( \
		source .venv/bin/activate; \
		python `which nosetests` -s --with-coverage --cover-erase --cover-package=. --cover-html --cover-html-dir=_build/coverage; \
	)

local:
	@rm -rf dist
	@( \
		python setup.py sdist; \
		pip install dist/helium*.tar.gz; \
	)

upload:
	@rm -rf dist
	@( \
		source .venv/bin/activate; \
		python setup.py sdist; \
		twine upload dist/*; \
	)
