build:
    poetry build

test:
    poetry run pytest

lint:
    poetry run ruff check .
    safety scan

deps:
    poetry show --outdated --top-level
