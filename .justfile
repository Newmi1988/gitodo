test:
  poetry run pytest --cov-report term-missing --cov=src tests/

format:
  black ./src
  isort .

