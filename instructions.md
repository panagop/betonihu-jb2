You are helping me set up a Jupyter Book v2 project from scratch. Please follow
these exact specifications:

## Stack
- Python manager: uv (https://docs.astral.sh/uv/)
- Jupyter Book version: 2.x (>=2.0.0), which is built on MyST-MD (not Sphinx)
- IDE: VS Code
- Deployment target: GitHub Pages via GitHub Actions

---

## STEP 1 — Project Initialization

1. Initialize a new uv project:
   uv init my-book
   cd my-book

2. Create and activate a virtual environment:
   uv venv
   # On Windows: .venv\Scripts\activate
   # On macOS/Linux: source .venv/bin/activate

3. Add jupyter-book v2 and ipykernel as dependencies:
   uv add "jupyter-book>=2.0.0"
   uv add --dev ipykernel

4. Verify the installation:
   uv run jupyter-book --version

---

## STEP 2 — Initialize the Book

1. Run the interactive init command to scaffold the project:
   uv run jupyter-book init

   This creates the following structure:
   my-book/
   ├── myst.yml          ← main configuration (replaces _config.yml + _toc.yml)
   ├── intro.md          ← landing page
   ├── notebooks/        ← folder for .ipynb or .md content files
   └── _build/           ← output folder (auto-generated, add to .gitignore)

2. Note: Jupyter Book v2 uses myst.yml for ALL configuration. There is NO
   _config.yml or _toc.yml as in v1. The table of contents is defined inside
   myst.yml under the "project.chapters" key.

---

## STEP 3 — Configure myst.yml

Create/edit myst.yml as follows (customize the fields in angle brackets):

version: 1
project:
  title: <Your Book Title>
  authors:
    - name: <Your Name>
  github: https://github.com/<your-username>/<your-repo>
  chapters:
    - file: intro.md
    - file: notebooks/chapter1.md
    # add more files here

site:
  template: book-theme

---

## STEP 4 — Build Locally

Build the book to verify everything works:
   uv run jupyter-book build .

The output is generated in _build/html/. Open _build/html/index.html in your
browser to preview.

For live preview during writing:
   uv run jupyter-book start .

---

## STEP 5 — VS Code Integration

1. Register the uv virtual environment as a Jupyter kernel so VS Code can use it:
   uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=my-book

2. Install the "Jupyter" VS Code extension (ms-toolsai.jupyter) if not already installed.

3. In VS Code, when opening a .ipynb file, select the kernel named "my-book"
   from the kernel picker (top-right of the notebook editor).

4. Add a .vscode/settings.json to auto-select the environment:
   {
     "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
   }
   (On Windows use: "${workspaceFolder}\\.venv\\Scripts\\python.exe")

---

## STEP 6 — Git Setup

1. Initialize git:
   git init
   git branch -M main

2. Create a .gitignore file with at least:
   .venv/
   _build/
   __pycache__/
   .jupyter_cache/
   *.pyc

3. Create the GitHub repository and push:
   git add .
   git commit -m "Initial Jupyter Book v2 setup"
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main

---

## STEP 7 — GitHub Actions for GitHub Pages

1. Generate the GitHub Actions workflow file automatically:
   uv run jupyter-book github-pages

   This creates .github/workflows/deploy.yml automatically.

2. If the command above is not available in your version, create the file
   manually at .github/workflows/deploy.yml with this content:

name: Deploy Jupyter Book to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install

      - name: Install dependencies
        run: uv sync

      - name: Build Jupyter Book
        run: uv run jupyter-book build .

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: _build/html

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

3. Commit and push:
   git add .github/
   git commit -m "Add GitHub Pages deployment workflow"
   git push

---

## STEP 8 — Enable GitHub Pages

In your GitHub repository:
1. Go to Settings → Pages
2. Under "Source", select: GitHub Actions (not "Deploy from a branch")
3. Save.

The next push to main will trigger the workflow and publish the book at:
https://<your-username>.github.io/<your-repo>/

---

## IMPORTANT NOTES about Jupyter Book v2 vs v1

- Config file is myst.yml, NOT _config.yml
- Table of contents is inside myst.yml, NOT _toc.yml
- Built on MyST-MD engine, NOT Sphinx
- CLI command is still: jupyter-book (or jb)
- Build output directory is _build/html/ (same as v1)
- GitHub Actions source must be set to "GitHub Actions" (not gh-pages branch)

---

## pyproject.toml Reference

After running uv init + uv add, your pyproject.toml should look like this:

[project]
name = "my-book"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "jupyter-book>=2.0.0",
]

[dependency-groups]
dev = [
    "ipykernel>=6.0.0",
]

Do not manually edit the uv.lock file. Always use uv add / uv remove to manage
dependencies.

---

Please scaffold this project now, creating all necessary files. Ask me for my
book title and GitHub username before generating myst.yml and the workflow file.

