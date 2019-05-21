.PHONY: isort
isort:
	@echo -n "Run isort"
	isort -rc marshmallow_url_params_schema
	isort -rc tests


.flake: $(shell find marshmallow_url_params_schema -type f) $(shell find tests -type f)
	flake8 marshmallow_url_params_schema tests
	@if ! isort -c -rc marshmallow_url_params_schema tests; then \
            echo "Import sort errors, run 'make isort' to fix them!!!"; \
            isort --diff -rc marshmallow_url_params_schema tests; \
            false; \
	fi

.PHONY: flake
flake: .flake
	@echo -n "Run flake and isort"

.PHONY: test
test:
	@echo -n "Run tests"
	$(eval export PYTHONPATH=.)
	py.test -svvv -rs

.PHONY: init-env
init-env:
	@if [ ! -d "./bin" ]; then \
		virtualenv --prompt="(marshmallow-url-params) " .virtualenv; \
	fi
	. .virtualenv/bin/activate

.PHONY: install
install:
	@./setup.py install
	@pip install -e ".[testing]"
	echo "Libraries have been planted"

.PHONY: update
upload:
	echo -n "Build and upload package to Nexus PyPi"
	@./setup.py sdist
	@twine upload dist/*

.PHONY: clean
clean:
	@echo -n "Clear temp files"
	@rm -rf `find . -name __pycache__`
	@rm -rf `find . -name .tox`
	@rm -rf `find . -name *.egg-info`
	@rm -rf `find . -name .pytest_cache`
	@rm -rf `find . -name .cache`
	@rm -rf `find . -name htmlcov`
	@rm -rf `find . -name .coverage`
	@rm -rf `find . -name dist`
	@rm -rf `find . -name build`
	@python setup.py clean
