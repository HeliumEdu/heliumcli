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
		python -m pip install -r requirements-dev.txt; \
	)

test: virtualenv
	@( \
		source .venv/bin/activate; \
		python -m coverage run -m unittest discover -b && python -m coverage xml && python -m coverage html && python -m coverage report; \
	)

local:
	@rm -rf dist
	@( \
		$(PYTHON_BIN) setup.py sdist; \
		$(PYTHON_BIN) -m pip install dist/*.tar.gz; \
	)

validate-release:
	@if [[ "${VERSION}" == "" ]]; then echo "VERSION is not set" & exit 1 ; fi

	@if [[ $$(grep "__version__ = \"${VERSION}\"" heliumcli/settings.py) == "" ]] ; then echo "Version not bumped in heliumcli/settings.py" & exit 1 ; fi

upload:
	@rm -rf *.egg-info dist
	@( \
		source .venv/bin/activate; \
		python -m pip install twine; \
		python setup.py sdist; \
		python -m twine upload dist/*; \
	)
