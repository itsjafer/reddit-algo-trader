PYTHON = python3

.PHONY = setup run clean

setup:
	( \
		pip install tox; \
		tox -e venv; \
	)

run_analysis:
	( \
		. venv/bin/activate; \
		python3 stock_analysis.py; \
	)

run_trade:
	( \
		. venv/bin/activate; \
		python3 trading.py; \
	)

clean:
	rm -rf venv
