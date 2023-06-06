build:
    poetry build

test:
    poetry run pytest

lint:
    poetry run ruff check .
