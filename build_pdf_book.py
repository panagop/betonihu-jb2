"""Build PDF book from MyST-generated LaTeX using plain_latex_book template.

MyST v1.8.x has a bug where Greek Unicode characters in headings and
verbatim blocks are converted to LaTeX math commands (e.g. Π → \\Pi).
This script:
1. Runs `jupyter-book build --pdf` to generate TeX files (book class)
2. Fixes Greek characters in all generated .tex files
3. Adds fontspec/polyglossia for XeLaTeX Greek support
4. Compiles with xelatex + bibtex

Usage: uv run python build_pdf_book.py

Requires:
- myst.yml exports with template: plain_latex_book and toc: pdf_toc.yml
- MiKTeX installed (xelatex, bibtex)
"""

import re
import subprocess
import sys
from pathlib import Path

# Greek letter mappings: LaTeX math command → Unicode character
GREEK_MAP = {
    # Uppercase
    r"\Alpha": "Α", r"\Beta": "Β", r"\Gamma": "Γ", r"\Delta": "Δ",
    r"\Epsilon": "Ε", r"\Zeta": "Ζ", r"\Eta": "Η", r"\Theta": "Θ",
    r"\Iota": "Ι", r"\Kappa": "Κ", r"\Lambda": "Λ", r"\Mu": "Μ",
    r"\Nu": "Ν", r"\Xi": "Ξ", r"\Omicron": "Ο", r"\Pi": "Π",
    r"\Rho": "Ρ", r"\Sigma": "Σ", r"\Tau": "Τ", r"\Upsilon": "Υ",
    r"\Phi": "Φ", r"\Chi": "Χ", r"\Psi": "Ψ", r"\Omega": "Ω",
    # Lowercase
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\zeta": "ζ", r"\eta": "η", r"\theta": "θ",
    r"\iota": "ι", r"\kappa": "κ", r"\lambda": "λ", r"\mu": "μ",
    r"\nu": "ν", r"\xi": "ξ", r"\omicron": "ο", r"\pi": "π",
    r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ", r"\upsilon": "υ",
    r"\phi": "φ", r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\varepsilon": "ε", r"\varphi": "φ",
}

TEX_DIR = Path("exports/betonihu-book_pdf_tex")
OUTPUT_PDF = Path("exports/betonihu-book.pdf")
NOTEBOOKS_DIR = Path("notebooks")


def find_notebook_for_tex(tex_file: Path) -> Path | None:
    """Find the .ipynb source for a TeX file, if any."""
    for nb_path in NOTEBOOKS_DIR.glob("*.ipynb"):
        nb_name = nb_path.stem.replace("_", "-")
        if tex_file.stem.endswith(nb_name):
            return nb_path
    return None


def fix_verbatim_from_notebook(content: str, notebook_path: Path) -> str:
    """Replace mangled verbatim blocks with original notebook cell content."""
    import json

    nb = json.load(open(notebook_path, "r", encoding="utf-8"))

    # Build ordered list: for each code cell, source text then output text
    originals = []
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            originals.append("".join(cell["source"]))
            for output in cell.get("outputs", []):
                text = None
                if output.get("output_type") == "stream":
                    text = "".join(output.get("text", []))
                elif output.get("output_type") == "execute_result":
                    data = output.get("data", {})
                    if "text/plain" in data:
                        d = data["text/plain"]
                        text = "".join(d) if isinstance(d, list) else d
                # Skip display_data with images (e.g. matplotlib figures)
                # — their text/plain repr doesn't appear as verbatim in TeX
                if text:
                    originals.append(text)

    # Find verbatim blocks in TeX
    pattern = re.compile(r"\\begin\{verbatim\}\n(.*?)\\end\{verbatim\}", re.DOTALL)
    matches = list(pattern.finditer(content))

    if len(matches) != len(originals):
        print(f"  WARNING: Verbatim/cell mismatch: {len(matches)} blocks vs {len(originals)} expected")
        return content

    # Replace in reverse order to preserve string positions
    for match, orig in reversed(list(zip(matches, originals))):
        orig_text = orig.rstrip("\n") + "\n"
        replacement = f"\\begin{{verbatim}}\n{orig_text}\\end{{verbatim}}"
        content = content[:match.start()] + replacement + content[match.end():]

    return content


def fix_greek_in_text(content: str) -> str:
    """Replace LaTeX math Greek commands with Unicode.

    MyST wraps Greek text in $...$ math mode, e.g.:
      $\\Pi\\alpha\\rho$ά$\\delta\\epsilon\\iota\\gamma\\mu\\alpha$
    for the word "Παράδειγμα". We detect $...$ blocks that contain
    ONLY Greek letter commands (no real math like subscripts, fractions)
    and convert them to plain Unicode.

    Also fixes Greek commands inside \\text{} blocks within math mode,
    since \\text{} is a text context where Unicode works under XeLaTeX.
    """

    def replace_greek_commands(s: str) -> str:
        """Replace all Greek LaTeX commands with Unicode characters."""
        for cmd, char in sorted(GREEK_MAP.items(), key=lambda x: -len(x[0])):
            s = s.replace(cmd, char)
        return s

    def is_greek_only_math(math_content: str) -> bool:
        """Check if a $...$ block contains only Greek letter commands."""
        stripped = math_content
        for cmd in sorted(GREEK_MAP.keys(), key=lambda x: -len(x)):
            stripped = stripped.replace(cmd, "")
        stripped = stripped.strip()
        remaining = re.sub(r"[A-Za-z]", "", stripped)
        return remaining == ""

    def replace_greek_math(match: re.Match) -> str:
        """Replace a $...$ block with Unicode if it's just Greek text."""
        inner = match.group(1)
        if is_greek_only_math(inner):
            return replace_greek_commands(inner)
        return match.group(0)

    # First, fix Greek commands inside \text{} blocks (even within math)
    def fix_text_block(match: re.Match) -> str:
        inner = match.group(1)
        return "\\text{" + replace_greek_commands(inner) + "}"

    content = re.sub(r"\\text\{([^}]*)\}", fix_text_block, content)

    # Replace $...$ blocks that are just Greek text
    content = re.sub(r"\$([^$]+)\$", replace_greek_math, content)

    # Also fix Greek commands in plain text (outside any $...$)
    parts = re.split(r"(\$[^$]+\$)", content)
    for i, part in enumerate(parts):
        if not part.startswith("$"):
            parts[i] = replace_greek_commands(part)

    return "".join(parts)


def add_bookmarksnumbered(content: str) -> str:
    """Add bookmarksnumbered option to hypersetup so PDF bookmarks show section numbers."""
    content = content.replace(
        "\\hypersetup{\n  colorlinks,",
        "\\hypersetup{\n  bookmarksnumbered=true,\n  colorlinks,",
        1,
    )
    return content


def add_xelatex_preamble(content: str) -> str:
    """Add fontspec and polyglossia packages for XeLaTeX Greek support.

    Handles the book document class from plain_latex_book template.
    Also removes pdflatex-only packages that conflict with XeLaTeX.
    """
    preamble = (
        "\n\\usepackage{fontspec}\n"
        "\\usepackage{amssymb}\n"
        "\\usepackage{polyglossia}\n"
        "\\setdefaultlanguage{greek}\n"
        "\\setotherlanguage{english}\n"
        "\\setmainfont{Fira Sans}\n"
        "\\setsansfont{Fira Sans}\n"
        "\\setmonofont{Fira Mono}\n"
        "\\newfontfamily\\greekfonttt{Cascadia Mono}\n"
        "\n% Framed code blocks with smaller monospace font\n"
        "\\usepackage{fancyvrb}\n"
        "\\usepackage{xcolor}\n"
        "\\usepackage{mdframed}\n"
        "\\DefineVerbatimEnvironment{Highlighting}{Verbatim}{}\n"
        "\\let\\oldverbatim\\verbatim\n"
        "\\let\\endoldverbatim\\endverbatim\n"
        "\\renewenvironment{verbatim}{\\footnotesize\\oldverbatim}{\\endoldverbatim}\n"
        "\\surroundwithmdframed[\n"
        "  linewidth=0.5pt,\n"
        "  linecolor=gray!50,\n"
        "  backgroundcolor=gray!5,\n"
        "  innerleftmargin=8pt,\n"
        "  innerrightmargin=8pt,\n"
        "  innertopmargin=6pt,\n"
        "  innerbottommargin=6pt\n"
        "]{verbatim}\n"
    )

    # Find the \documentclass line and insert preamble after it
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("\\documentclass"):
            lines.insert(i + 1, preamble)
            break
    else:
        print("  WARNING: No \\documentclass found, inserting preamble at top")
        lines.insert(0, preamble)

    content = "\n".join(lines)

    # Remove pdflatex-only packages that conflict with XeLaTeX/fontspec
    for pkg in [
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{lmodern}",
    ]:
        content = content.replace(pkg, "% " + pkg + "  % removed for XeLaTeX")

    return content


def main():
    # Step 1: Generate TeX files
    print("[1/4] Generating TeX files (book template)...")
    result = subprocess.run(
        ["uv", "run", "jupyter-book", "build", "--pdf"],
        capture_output=False,
    )
    # The PDF step may fail (we compile ourselves), but TeX files are generated

    if not TEX_DIR.exists():
        print(f"ERROR: TeX directory not found: {TEX_DIR}")
        sys.exit(1)

    # Step 2: Fix Greek characters in all .tex files
    print("\n[2/4] Fixing Greek characters in TeX files...")
    tex_files = list(TEX_DIR.glob("*.tex"))
    for tex_file in tex_files:
        content = tex_file.read_text(encoding="utf-8")
        original = content

        # First, fix verbatim blocks from original notebook if available
        notebook_path = find_notebook_for_tex(tex_file)
        if notebook_path:
            content = fix_verbatim_from_notebook(content, notebook_path)
            print(f"    (restored verbatim from {notebook_path.name})")

        content = fix_greek_in_text(content)

        # Add XeLaTeX preamble only to the main file
        if tex_file.name == "betonihu-book.tex":
            content = add_xelatex_preamble(content)
            content = add_bookmarksnumbered(content)

        if content != original:
            tex_file.write_text(content, encoding="utf-8")
            print(f"  + Fixed: {tex_file.name}")
        else:
            print(f"  - Unchanged: {tex_file.name}")

    # Step 3: Compile with xelatex
    print("\n[3/4] Compiling with XeLaTeX...")
    main_tex = TEX_DIR / "betonihu-book.tex"

    for run_num in range(1, 4):  # Run xelatex up to 3 times for references
        print(f"  Pass {run_num}/3...")
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
            cwd=TEX_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            print(f"  WARNING: XeLaTeX pass {run_num} had warnings/errors")
            # Check for fatal errors
            if "Fatal error" in result.stdout or "Emergency stop" in result.stdout:
                print(f"ERROR: XeLaTeX fatal error. Check {TEX_DIR / 'betonihu-book.log'}")
                # Print last 30 lines of log for context
                log_lines = result.stdout.strip().split("\n")
                for line in log_lines[-30:]:
                    print(f"    {line}")
                sys.exit(1)

        # Run bibtex after first pass
        if run_num == 1:
            print("  Running BibTeX...")
            subprocess.run(
                ["bibtex", "betonihu-book"],
                cwd=TEX_DIR,
                capture_output=True,
            )

    # Step 4: Copy PDF to output
    pdf_in_tex_dir = TEX_DIR / "betonihu-book.pdf"
    if pdf_in_tex_dir.exists():
        import shutil
        OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_in_tex_dir, OUTPUT_PDF)
        size_kb = OUTPUT_PDF.stat().st_size / 1024
        print(f"\n[4/4] PDF generated: {OUTPUT_PDF} ({size_kb:.0f} KB)")
    else:
        print(f"\nERROR: PDF not found. Check logs in {TEX_DIR}")
        sys.exit(1)


if __name__ == "__main__":
    main()
