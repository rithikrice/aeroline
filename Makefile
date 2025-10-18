.PHONY: setup fmt test run-api run-ui snow-init seed snowpark-setup snowpark-status clean

# Setup virtual environment and install dependencies
setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt

# Format and lint code
fmt:
	. .venv/bin/activate && ruff check --fix .
	. .venv/bin/activate && ruff format .
	. .venv/bin/activate && mypy app/ --ignore-missing-imports

# Run tests
test:
	. .venv/bin/activate && pytest tests/ -v

# Run FastAPI backend
run-api:
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8080

# Run Streamlit UI
run-ui:
	. .venv/bin/activate && streamlit run ui/streamlit_app.py

# Initialize Snowflake database objects
snow-init:
	@echo "Initializing Snowflake database objects..."
	@for file in snow/*.sql; do \
		echo "Running $$file..."; \
		. .venv/bin/activate && python -c "from app.snowflake_client import SnowflakeClient; \
		import os; \
		from dotenv import load_dotenv; \
		load_dotenv(); \
		with SnowflakeClient() as client: \
			with open('$$file', 'r') as f: \
				sql = f.read(); \
				for statement in sql.split(';'): \
					statement = statement.strip(); \
					if statement: \
						print(f'Executing: {statement[:50]}...'); \
						client.execute_sql(statement)"; \
	done

# Seed sample data
seed:
	@echo "Seeding sample data..."
	. .venv/bin/activate && python -c "from app.snowflake_client import SnowflakeClient; \
	from dotenv import load_dotenv; \
	load_dotenv(); \
	with SnowflakeClient() as client: \
		with open('snow/05_seed_sample.sql', 'r') as f: \
			sql = f.read(); \
			for statement in sql.split(';'): \
				statement = statement.strip(); \
				if statement: \
					print(f'Executing: {statement[:50]}...'); \
					client.execute_sql(statement)"

# Setup Snowpark integration (stages, UDFs, procedures)
snowpark-setup:
	@echo "Setting up Snowpark integration..."
	. .venv/bin/activate && python scripts/setup_snowpark.py

# Check Snowpark status via API
snowpark-status:
	@echo "Checking Snowpark status..."
	@curl -s http://localhost:8080/snowpark/status -H "x-api-key: dev-key-123" | python -m json.tool

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
