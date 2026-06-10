# this is an optional command runner using the "just" cli tool to make a starting server's
# and complex command easier

# more info on how to install here: https://github.com/casey/just#packages
# or run: `uv tool install rust-just`
# then run a recipe like 'just run' in your console

PYTHON := `command -v uv >/dev/null 2>&1 && echo "uv run" || echo "python3.14 -m"`
PIP := `command -v uv >/dev/null 2>&1 && echo "uv pip" || echo "python3.14 -m pip"`

# run the main script
run:
    {{ PYTHON }} main.py

# run the test suite
test:
    {{ PYTHON }} pytest -v

# format, lint and type check the code
check:
    ruff format . && ruff check .
    ty check .

install-deps:
    command -v uv >/dev/null 2>&1 && echo "uv run sync" || echo "python3.14 -m pip-r requirements-dev.txt "

# update dependencies
update-dependencies:
    {{ PIP }} compile pyproject.toml -o requirements.txt
    {{ PIP }} compile pyproject.toml --group dev -o requirements-dev.txt
