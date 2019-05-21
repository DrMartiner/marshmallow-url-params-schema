# Introduction
[![Build Status](https://travis-ci.org/DrMartiner/marshmallow-url-params-schema.svg?branch=master)](https://travis-ci.org/DrMartiner/marshmallow-url-params-schema)
[![PyPI version](https://badge.fury.io/py/marshmallow-url-params-schema.svg)](https://badge.fury.io/py/marshmallow-url-params-schema)
[![GitHub version](https://badge.fury.io/gh/DrMartiner%2Fmarshmallow-url-params-schema.svg)](https://badge.fury.io/gh/DrMartiner%2Fmarshmallow-url-params-schema)
[![Requirements Status](https://requires.io/github/DrMartiner/marshmallow-url-params-schema/requirements.svg?branch=master)](https://requires.io/github/DrMartiner/marshmallow-url-params-schema/requirements/?branch=master)

# For developing

## Beginning to develop
```bash
make init-env
make install

# To added Flake8's pre-hook
flake8 --install-hook git
git config --bool flake8.strict true
```

## Before your commit
```bash
make isort flake
```

## To upload new version
```bash
# Bump version at setup.py
make upload
make clean
```