import nbformat
from pathlib import Path
import re

# Base URL for raw images in GitHub
GITHUB_RAW_BASE = "https://github.com/fastai/fastbook/blob/master/images/"

# Regex patterns to match Markdown and HTML image links
md_pattern = re.compile(r'!\[([^\]]*)\]\((?:\.\./)?images/([^)]+)\)')
html_pattern = re.compile(r'<img([^>]+)src=[\'"](?:\.\./)?images/([^\'"]+)[\'"]([^>]*)>')

def fix_image_links_in_markdown(source: str) -> str:
    # Fix Markdown-style image links
    source = md_pattern.sub(
        lambda m: f'![{m.group(1)}]({GITHUB_RAW_BASE}{m.group(2)}?raw=true)', source
    )
    # Fix raw HTML <img> tags
    source = html_pattern.sub(
        lambda m: f'<img{m.group(1)}src="{GITHUB_RAW_BASE}{m.group(2)}?raw=true"{m.group(3)}>',
        source
    )
    return source

def update_imgs(nb) -> bool:
    modified = False
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            new_source = fix_image_links_in_markdown(cell.source)
            if new_source != cell.source:
                cell.source = new_source
                modified = True
    return modified

# The block of code to insert if missing
SETUP_CODE = """\
# ✅ Kaggle/Colab/Local compatible setup
!git clone https://github.com/fastai/fastbook.git
%cd fastbook
"""

def setup_already_present(nb) -> bool:
    return any(
        cell.cell_type == "code" and "!git clone https://github.com/fastai/fastbook.git" in cell.source
        for cell in nb.cells
    )

def add_setup_block(nb) -> bool:
    if setup_already_present(nb):
        return False
    setup_cell = nbformat.v4.new_code_cell(SETUP_CODE)
    nb.cells.insert(0, setup_cell)
    return True

def process_notebook(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        changed_imgs = update_imgs(nb)
        added_setup = add_setup_block(nb)

        if changed_imgs or added_setup:
            with path.open("w", encoding="utf-8") as f:
                nbformat.write(nb, f)
            print(f"✅ Updated: {path}")
        else:
            print(f"✔ No changes needed: {path}")
    except Exception as e:
        print(f"❌ Error processing {path}: {e}")

def process_all_notebooks(notebook_dir: Path):
    for nb_path in notebook_dir.rglob("*.ipynb"):
        process_notebook(nb_path)

# Example usage
if __name__ == "__main__":
    process_all_notebooks(Path("./"))
