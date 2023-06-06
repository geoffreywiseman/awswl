build:
    poetry build

test:
    poetry run pytest

lint:
    poetry run ruff check .

deps:
    poetry show --outdated --top-level
