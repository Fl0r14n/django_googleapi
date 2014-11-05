.PHONY: clean-pyc
MANAGE_PATH=python ./manage.py

clean-pyc:
	find . -name '*.pyc' | xargs rm

bootstrap:
	pip install -r requirements.txt

test:
	$(MANAGE_PATH) test

runserver:
	$(MANAGE_PATH) runserver


