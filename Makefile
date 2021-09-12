PYTHON = python3
VENV_DIR = .venv
VENV_PIP = $(VENV_DIR)/bin/pip
VENV_PYTHON = $(VENV_DIR)/bin/python

.PHONY: wheel
wheel:
	$(VENV_PYTHON) setup.py bdist_wheel

.PHONY: sdist
sdist:
	$(VENV_PYTHON) setup.py sdist

.PHONY: setup
setup:
	rm -rf $(VENV_DIR)
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install -r requirements.txt

.PHONY: clean
clean:
	rm -rf $(VENV_DIR) build dist *.egg-info pydoc \
	.pytest .pytest_cache coverage.xml .coverage

.PHONY: check
check:
	$(VENV_PYTHON) -m pytest

.PHONY: html
html: \
 $(shell find mir -name __init__.py -printf "%h.html\n" | sed 's:/:.:g; s:^:pydoc/:') \
 $(shell find mir -name '*.py' ! -name __init__.py | sed 's:/:.:g; s/\.py/\.html/; s:^:pydoc/:')

pydoc/%.html: $(wildcard mir/**/*.py)
	mkdir -p pydoc
	$(VENV_PYTHON) -m pydoc -w $(@F:%.html=%)
	mv $(@F) $@

.PHONY: upload
upload: sdist wheel
	$(VENV_PYTHON) -m twine upload --skip-existing dist/*
