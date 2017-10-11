PYTHON := pipenv run python
export PYTHONPATH := $(CURDIR)

.PHONY: all
all:

.PHONY: check
check:
	$(PYTHON) -m pytest

.PHONY: sdist
sdist:
	$(PYTHON) setup.py sdist

.PHONY: wheel
wheel:
	$(PYTHON) setup.py bdist_wheel

.PHONY: html
html: \
 $(shell find mir -name __init__.py -printf "%h.html\n" | sed 's:/:.:g; s:^:doc/:') \
 $(shell find mir -name '*.py' ! -name __init__.py | sed 's:/:.:g; s/\.py/\.html/; s:^:doc/:')

doc/%.html: $(wildcard mir/**/*.py)
	mkdir -p doc
	cd doc && $(PYTHON) -m pydoc -w $(@F:%.html=%)

.PHONY: TAGS
TAGS:
	ctags -e -R mir

.PHONY: distclean
distclean:
	rm -rf build dist doc *.egg-info
	rm -f .coverage

.PHONY: upload
upload: sdist wheel
	$(PYTHON) -m twine upload --skip-existing dist/*

.PHONY: pipenv
pipenv:
	pipenv install --dev
