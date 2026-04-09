# Copilot Instructions for betonihu-jb2

## Project Overview
Jupyter Book v2 project for reinforced concrete design notes (Eurocode 2).
- GitHub: https://github.com/panagop/betonihu-jb2
- Live site: https://panagop.github.io/betonihu-jb2/

## Stack
- Python managed with **uv** (not pip/conda)
- **Jupyter Book v2** (MyST-MD engine, NOT Sphinx)
- Config: `myst.yml` (no `_config.yml` or `_toc.yml`)
- Deploy: GitHub Pages via GitHub Actions
- Custom Python package: `src/betonihu/` (installed via hatchling)

## Key Commands
- `uv run jupyter-book start .` — live preview (keeps server running)
- `uv run jupyter-book build --html` — static build (exits after build)
- `uv sync` — install/update dependencies
- `uv add <pkg>` — add dependency

## Project Structure
```
myst.yml              ← all config + TOC (no _config.yml or _toc.yml)
references.bib        ← BibTeX bibliography
requirements.txt      ← for Binder (includes -e .)
custom.css            ← light-mode fix for thebe output
pyproject.toml        ← hatchling build, src layout
src/betonihu/         ← installable Python package (EC2 concrete/steel utilities)
notebooks/            ← chapter .md and .ipynb files
.github/workflows/deploy.yml ← GitHub Pages deployment
```

## Custom Package: betonihu
- `src/betonihu/concrete.py` — ConcreteProperties dataclass, fcd() helper
- `src/betonihu/steel.py` — SteelProperties dataclass, fyd() helper
- Binder users get it via `-e .` in requirements.txt

## Known Gotchas
- **UTF-8 BOM breaks MyST frontmatter**: VS Code on Windows may add BOM to new .md files. MyST can't parse `---` frontmatter with a BOM. Always ensure files are UTF-8 without BOM. Check with: `[System.IO.File]::ReadAllBytes("file.md")[0..2]` — should NOT be `EF BB BF`.
- **BASE_URL for GitHub Pages**: Must be set as an environment variable in deploy.yml, not in myst.yml. Value: `/${{ github.event.repository.name }}`.
- **Binder**: Needs `requirements.txt` (doesn't support uv/pyproject.toml natively). Include `-e .` to install the local package.
- **Thebe output dark in light mode**: Fixed via custom.css targeting JupyterLab classes with `:root:not(.dark)` selectors.
- **No `{bibliography}` directive in MyST-MD**: References appear automatically at bottom of pages. Use `@key` pandoc syntax to cite BibTeX entries.
- **Frontmatter**: Use `---` YAML frontmatter for title, or use `# Heading`. Don't use both — it duplicates the title.
- **TOC nesting**: Use `children:` key under a `file:` entry in myst.yml for subsections.

## Conventions
- New .md files: always check for BOM before committing
- When adding dependencies: use `uv add`, then also update `requirements.txt` for Binder
- When adding new pages: add to `toc:` in myst.yml
- When adding new BibTeX entries: add to references.bib
