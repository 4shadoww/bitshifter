.DEFAULT_GOAL := build

build:
	python -m build

check:
	ruff check

clean:
	rm -r dist
	rm -r bitshifter.egg-info
