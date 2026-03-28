.PHONY: help install install-dev test test-cov lint format clean build docs

help:
	@echo "HorseClaw Development Commands:"
	@echo "  make install      - Install package"
	@echo "  make install-dev  - Install with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build package"
	@echo "  make docs         - Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=term --cov-report=html

lint:
	flake8 src tests --max-line-length=100
	mypy src/horseclaw

format:
	black src tests --line-length=100

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docs:
	cd docs && make html

demo:
	python examples/usage_demo.py

run-cli:
	python horseclaw_cli.py status
