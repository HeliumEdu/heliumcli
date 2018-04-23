.PHONY: all env virtualenv install

SHELL := /usr/bin/env bash

all: env virtualenv install

virtualenv:
	@if [ ! -d ".venv" ]; then \
		python3 -m pip install virtualenv --user; \
        python3 -m virtualenv .venv; \
	fi

install: env virtualenv
	@( \
		source .venv/bin/activate; \
		python -m pip install -r requirements.txt; \
	)

test: virtualenv
	@( \
		source .venv/bin/activate; \
		python `which nosetests` --with-coverage --cover-erase --cover-package=. --cover-html --cover-html-dir=htmlcov; \
	)
