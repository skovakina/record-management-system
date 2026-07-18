# Record Management System

## Prerequisites

1. Install [Homebrew](https://brew.sh/)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install matching Python and Tkinter versions (macOS).
> Important: Use the same version for `python` and `python-tk`.

```bash
brew install python@3.14 python-tk@3.14
```

## Run the app

From the project directory:

```bash
$(brew --prefix)/bin/python3.14 -m venv --clear .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py
```

## Run tests

From the project directory:

Activate venv

```bash
source .venv/bin/activate
```

```bash
python -m unittest discover -s tests
```

Run one test file:

```bash
python -m unittest tests.test_app
```

Run tests with coverage:

```bash
python -m coverage run --source=src -m unittest discover -s tests && python -m coverage report -m
```
