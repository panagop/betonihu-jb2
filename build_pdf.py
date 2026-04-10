"""Build PDF from MyST-generated LaTeX, fixing Greek character encoding.

MyST v1.8.x has a bug where Greek Unicode characters in headings and
verbatim blocks are converted to LaTeX math commands (e.g. Π → \\Pi).
This script:
1. Runs `jupyter-book build --pdf` to generate TeX files
2. Fixes Greek characters in all generated .tex files
3. Adds fontspec/polyglossia for XeLaTeX Greek support
4. Compiles with xelatex + bibtex

Usage: uv run python build_pdf.py
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


def fix_greek_in_text(content: str) -> str:
    """Replace LaTeX math Greek commands with Unicode.

    MyST wraps Greek text in $...$ math mode, e.g.:
      $\Pi\alpha\rho$ά$\delta\epsilon\iota\gamma\mu\alpha$
    for the word "Παράδειγμα". We detect $...$ blocks that contain
    ONLY Greek letter commands (no real math like subscripts, fractions)
    and convert them to plain Unicode.
    """

    def is_greek_only_math(math_content: str) -> bool:
        """Check if a $...$ block contains only Greek letter commands."""
        stripped = math_content
        for cmd in sorted(GREEK_MAP.keys(), key=lambda x: -len(x)):
            stripped = stripped.replace(cmd, "")
        # After removing all Greek commands, only whitespace/empty should remain
        # Real math has: _, ^, {, }, \frac, \cdot, digits, operators, etc.
        stripped = stripped.strip()
        # Allow single Latin letters (like E, A, H, N) that appear in Greek text
        remaining = re.sub(r"[A-Za-z]", "", stripped)
        return remaining == ""

    def replace_greek_math(match: re.Match) -> str:
        """Replace a $...$ block with Unicode if it's just Greek text."""
        inner = match.group(1)
        if is_greek_only_math(inner):
            result = inner
            for cmd, char in sorted(GREEK_MAP.items(), key=lambda x: -len(x[0])):
                result = result.replace(cmd, char)
            return result
        return match.group(0)  # Keep real math unchanged

    # Replace $...$ blocks that are just Greek text
    content = re.sub(r"\$([^$]+)\$", replace_greek_math, content)

    # Also fix Greek commands in plain text (outside any $...$)
    # Split on remaining $...$ blocks and fix non-math parts
    parts = re.split(r"(\$[^$]+\$)", content)
    for i, part in enumerate(parts):
        if not part.startswith("$"):
            for cmd, char in sorted(GREEK_MAP.items(), key=lambda x: -len(x[0])):
                part = part.replace(cmd, char)
            parts[i] = part

    return "".join(parts)


def add_xelatex_preamble(content: str) -> str:
    """Add fontspec and polyglossia packages for XeLaTeX Greek support."""
    preamble = (
        "\n\\usepackage{fontspec}\n"
        "\\usepackage{amssymb}\n"
        "\\usepackage{polyglossia}\n"
        "\\setdefaultlanguage{greek}\n"
        "\\setotherlanguage{english}\n"
        "\\setmainfont{Times New Roman}\n"
        "\\setsansfont{Calibri}\n"
        "\\setmonofont{Consolas}\n"
    )
    # Insert after \documentclass{...} line
    content = content.replace(
        "\\documentclass{article}",
        "\\documentclass{article}" + preamble,
        1,
    )
    return content


def main():
    # Step 1: Generate TeX files
    print("📑 Generating TeX files...")
    result = subprocess.run(
        ["uv", "run", "jupyter-book", "build", "--pdf"],
        capture_output=False,
    )
    # The PDF step will fail (no perl/latexmk), but TeX files are generated

    if not TEX_DIR.exists():
        print(f"❌ TeX directory not found: {TEX_DIR}")
        sys.exit(1)

    # Step 2: Fix Greek characters in all .tex files
    print("\n🔧 Fixing Greek characters in TeX files...")
    tex_files = list(TEX_DIR.glob("*.tex"))
    for tex_file in tex_files:
        content = tex_file.read_text(encoding="utf-8")
        original = content

        content = fix_greek_in_text(content)

        # Add XeLaTeX preamble only to the main file
        if tex_file.name == "betonihu-book.tex":
            content = add_xelatex_preamble(content)

        if content != original:
            tex_file.write_text(content, encoding="utf-8")
            print(f"  ✓ Fixed: {tex_file.name}")
        else:
            print(f"  - Unchanged: {tex_file.name}")

    # Step 3: Compile with xelatex
    print("\n🖨  Compiling with XeLaTeX...")
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
            print(f"  ⚠️  XeLaTeX pass {run_num} had warnings/errors")
            # Check for fatal errors
            if "Fatal error" in result.stdout or "Emergency stop" in result.stdout:
                print(f"❌ XeLaTeX fatal error. Check {TEX_DIR / 'betonihu-book.log'}")
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
        print(f"\n✅ PDF generated: {OUTPUT_PDF} ({size_kb:.0f} KB)")
    else:
        print(f"\n❌ PDF not found. Check logs in {TEX_DIR}")
        sys.exit(1)


if __name__ == "__main__":
    main()
