.PHONY: install run verify test dashboard clean

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

run:
	python main.py

verify:
	python scripts/verify_expected_results.py --results outputs/results_table.csv

test:
	pytest -q

dashboard:
	streamlit run app/dashboard.py

clean:
	find outputs -mindepth 1 -not -name .gitkeep -delete
	find data -mindepth 1 -not -name .gitkeep -delete
