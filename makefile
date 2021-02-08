PYTHON = python3

.PHONY = setup run clean

setup:
	( \
		pip install tox; \
		tox -e venv; \
	)

run:
	( \
		. venv/bin/activate; \
		python3 stock_analysis.py; \
	)

clean:
	rm -rf venv
