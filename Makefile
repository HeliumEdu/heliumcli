.PHONY: all virtualenv install test local upload

SHELL := /usr/bin/env bash
PYTHON_BIN ?= python

all: virtualenv install

virtualenv:
	@if [ ! -d ".venv" ]; then \
		$(PYTHON_BIN) -m pip install virtualenv --user; \
		$(PYTHON_BIN) -m virtualenv .venv; \
	fi

install: virtualenv
	@( \
		source .venv/bin/activate; \
		python -m pip install -r requirements.txt; \
	)

test: virtualenv
	@( \
		source .venv/bin/activate; \
		python `which nosetests` -s --with-coverage --cover-erase --cover-package=. --cover-html --cover-html-dir=htmlcov; \
	)

local:
	@rm -rf dist
	$(PYTHON_BIN) -m pip install click
	@
	@( \
		$(PYTHON_BIN) setup.py sdist; \
		$(PYTHON_BIN) -m pip install dist/heliumcli*.tar.gz; \
	)

upload:
	@rm -rf dist
	@( \
		source .venv/bin/activate; \
		python setup.py sdist; \
		twine upload dist/*; \
	)
