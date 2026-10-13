PORT ?= 5001
ARGS ?=

.DEFAULT_GOAL := help
.PHONY: help run stop sync lock upgrade add add-dev remove list tree test requirements shell clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ---- Server ----

run: ## Start the dev server (PORT=5001)
	uv run flask --app app run --debug --port $(PORT)

stop: ## Stop whatever is listening on PORT
	@pids=$$(lsof -ti tcp:$(PORT)); \
	if [ -n "$$pids" ]; then kill $$pids && echo "Stopped server on port $(PORT)"; \
	else echo "Nothing running on port $(PORT)"; fi

# ---- Dependencies ----

sync: ## Install dependencies from uv.lock into .venv
	uv sync

lock: ## Re-resolve pyproject.toml into uv.lock
	uv lock

upgrade: ## Upgrade all dependencies to their latest allowed versions
	uv lock --upgrade
	uv sync

add: ## Add a package: make add PKG=requests
	@test -n "$(PKG)" || { echo "Usage: make add PKG=<package>"; exit 1; }
	uv add $(PKG)

add-dev: ## Add a dev-only package: make add-dev PKG=ruff
	@test -n "$(PKG)" || { echo "Usage: make add-dev PKG=<package>"; exit 1; }
	uv add --dev $(PKG)

remove: ## Remove a package: make remove PKG=requests
	@test -n "$(PKG)" || { echo "Usage: make remove PKG=<package>"; exit 1; }
	uv remove $(PKG)

list: ## List installed packages
	uv pip list

tree: ## Show the dependency tree
	uv tree

requirements: ## Regenerate requirements.txt from uv.lock
	uv export --no-hashes --no-emit-project -o requirements.txt

# ---- Development ----

test: ## Run the tests (ARGS="-k name -x" for pytest options)
	uv run python -m pytest $(ARGS)

shell: ## Open a Python shell inside the project environment
	uv run python

clean: ## Remove caches and compiled files
	find . -path ./.venv -prune -o -type d \( -name __pycache__ -o -name .pytest_cache \) -print | xargs rm -rf
