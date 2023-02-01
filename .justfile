test:
  poetry run pytest --cov-report term-missing --cov=src tests/

fmt:
  black ./src
  black ./tests
  isort .

