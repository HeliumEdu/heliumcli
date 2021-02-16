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
		python `which nosetests` --with-coverage --cover-erase --cover-package=. --cover-xml --cover-xml-file=_build/coverage/coverage.xml --cover-html --cover-html-dir=_build/coverage; \
	)

local:
	@rm -rf dist
	@( \
		python setup.py sdist; \
		pip install dist/helium*.tar.gz; \
	)

validate-release:
	@if [[ "${VERSION}" == "" ]]; then echo "VERSION is not set" & exit 1 ; fi

	@if [[ $$(grep "__version__ = \"${VERSION}\"" heliumcli/settings.py) == "" ]] ; then echo "Version not bumped in heliumcli/settings.py" & exit 1 ; fi

upload:
	@rm -rf dist
	@( \
		source .venv/bin/activate; \
		python setup.py sdist; \
		twine upload dist/*; \
	)
