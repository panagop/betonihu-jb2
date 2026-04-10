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

## PDF Export (Local Only)
PDF export is local-only (not for GitHub Pages visitors). It uses XeLaTeX via MiKTeX.

### Prerequisites
- **MiKTeX** installed (provides `xelatex`, `bibtex`, and auto-installs missing LaTeX packages)
- No Perl needed (the build script bypasses `latexmk`)

### How to Build
```bash
uv run python build_pdf.py
```
Output: `exports/betonihu-book.pdf`

### How It Works
MyST v1.8.x has a bug where **Greek Unicode characters in headings and text are converted to LaTeX math commands** (e.g. `Π` → `\Pi`, `α` → `\alpha`). It also **mangles Greek text inside verbatim (code) blocks** by splitting characters with spaces. The `build_pdf.py` script works around both issues:
1. Runs `uv run jupyter-book build --pdf` to generate `.tex` files in `exports/betonihu-book_pdf_tex/`
2. For `.ipynb` files: restores verbatim blocks from original notebook cells (source + outputs), replacing the mangled TeX verbatim content
3. Post-processes all `.tex` files to convert Greek math commands back to Unicode in headings and body text
4. Adds XeLaTeX preamble (`fontspec`, `polyglossia`, `amssymb`, `geometry`, `mdframed`, `fancyvrb`) with Greek language support and fonts (Fira Sans, Fira Mono, Cascadia Mono for Greek monospace fallback)
5. Compiles with `xelatex` (3 passes + BibTeX for cross-references)

### Config
In `myst.yml`, the export format is set to `tex+pdf`:
```yaml
exports:
  - format: tex+pdf
    output: exports/betonihu-book.pdf
```

### Known Limitations
- **SVG images**: Need Inkscape for PDF conversion; falls back to PNG via ImageMagick
- **Iframes** (e.g. from `interactive_demo.md`): Cannot be rendered in PDF — ignored with a warning
- **Greek in math `\text{}`**: The `η` character inside `\text{ ή }` in math mode triggers a MyST warning (cosmetic, does not break the build)
- When the MyST Greek-to-Typst/LaTeX bug is fixed upstream, `build_pdf.py` can be replaced with a direct `uv run jupyter-book build --pdf` or `--typst` command
