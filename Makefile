jupyterlab:
	uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=bayesian-statistics
	uv run --with jupyter jupyter lab --port 4444


lint:
	@echo "--- 🧹 Running linters ---"
	uv run ruff format . 						        # running ruff formatting


# --- Session 1: linear regressions -------------------------------------------
figures:
	uv run python slides/figures.py

slides: figures
	uv run python slides/build_slides.py

notebooks:
	uv run python notebooks/build_notebooks.py

check-notebooks:
	uv run python notebooks/build_notebooks.py --execute

animations:
	uv run python animations/render.py

.PHONY: jupyterlab lint figures slides notebooks check-notebooks animations
