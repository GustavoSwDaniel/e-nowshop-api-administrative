.DEFAULT_GOAL := default_target

PROJECT_NAME := e-noewshop-api-employees
PYTHON_VERSION := 3.8.12
VENV_NAME := $(PROJECT_NAME)-$(PYTHON_VERSION)
COVERAGE := 75

create-venv:
	pyenv install -s $(PYTHON_VERSION)
	pyenv global ${PYTHON_VERSION}
	pyenv uninstall -f $(VENV_NAME)
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME)
	pyenv local $(VENV_NAME)
	pip install --upgrade pip
	poetry env use $(HOME)/.pyenv/versions/$(PYTHON_VERSION)/envs/$(VENV_NAME)/bin/python
	poetry install