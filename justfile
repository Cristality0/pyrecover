set windows-shell := ["powershell.exe", "-c"]
check: lint format typecheck test

# Run ruff linter
lint:
    uv run ruff check .

# Check code formatting
format:
    uv run ruff format --check .

# Run type checker
typecheck:
    uv run ty check

# Run tests with coverage
test:
    uv run pytest --cov=pyrecover --cov-report=term-missing -v

# Auto-fix lint and formatting issues
fix:
    uv run ruff check --fix .
    uv run ruff format .