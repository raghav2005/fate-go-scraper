# Makefile

.PHONY: run clean install-deps format

# Default target
run:
	@echo "Running retrieve_stuff.py..."
	@pipenv run python retrieve_stuff.py

# Clean target
clean:
	@echo "Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -r {} +

# Install dependencies target
install-deps:
	@echo "Installing dependencies..."
	@pipenv install --dev

# Format code with black
format:
	@echo "Formatting code with black..."
	@pipenv run black .

# Ensure pipenv environment is created
ensure-pipenv:
	@pipenv --venv || pipenv install --dev

# Install and run (optional)
install-and-run: ensure-pipenv install-deps run
