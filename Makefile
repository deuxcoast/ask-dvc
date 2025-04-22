VENV_PYTHON = .venv/bin/python

install:
	$(VENV_PYTHON) -m pip install -r requirements.txt

run-dev:
	$(VENV_PYTHON) manage.py runserver
