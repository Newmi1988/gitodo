test:
  poetry run pytest

format:
  black ./src
  isort .

