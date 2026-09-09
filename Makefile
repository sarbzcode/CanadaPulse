PYTHON ?= python
COMPOSE ?= docker compose

.PHONY: setup up down logs test lint status clean

setup:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

up:
	$(COMPOSE) up -d postgres

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f postgres

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

status:
	$(PYTHON) -m canadapulse.cli status

clean:
	$(PYTHON) -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('.pytest_cache', '.ruff_cache', 'htmlcov')]"

