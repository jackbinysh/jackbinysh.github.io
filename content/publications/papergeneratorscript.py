from pathlib import Path
import re
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


BIB_FILE = "mypapers.bib"
OUT_DIR = Path(".")
OVERWRITE = False


def slugify(text):
    text = text.replace("{", "").replace("}", "")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def clean_inline(text):
    return (
        text.replace("{", "")
        .replace("}", "")
        .replace("\n", " ")
        .replace('"', '\\"')
        .strip()
    )


def clean_block(text):
    """
    For YAML block strings. Do NOT escape quotes or backslashes.
    Keeps LaTeX-ish content much safer.
    """
    text = text.replace("\n", " ").strip()
    return text


def yaml_block(text, indent=2):
    pad = " " * indent
    if not text:
        return f"{pad}''"
    return "\n".join(f"{pad}{line}" for line in text.splitlines())


def parse_authors(entry):
    authors_raw = entry.get("author", "")
    authors = []

    for author in authors_raw.split(" and "):
        author = author.strip()

        if "," in author:
            last, first = [x.strip() for x in author.split(",", 1)]
            author = f"{first} {last}"

        authors.append(clean_inline(author))

    return authors


with open(BIB_FILE, encoding="utf-8") as f:
    bib = bibtexparser.load(f)


for entry in bib.entries:

    title = clean_inline(entry.get("title", "Untitled"))
    year = clean_inline(entry.get("year", "1900"))
    journal = clean_inline(entry.get("journal") or entry.get("booktitle", ""))
    abstract = clean_block(entry.get("abstract", ""))
    doi = clean_inline(entry.get("doi", ""))
    url = clean_inline(entry.get("url", ""))
    eprint = clean_inline(entry.get("eprint", ""))

    authors = parse_authors(entry)

    slug = slugify(title)
    folder = OUT_DIR / slug

    if folder.exists() and not OVERWRITE:
        print(f"Skipping existing folder: {folder}")
        continue

    folder.mkdir(parents=True, exist_ok=True)

    # Write individual cite.bib
    db = BibDatabase()
    db.entries = [entry]

    writer = BibTexWriter()
    writer.indent = "  "

    with open(folder / "cite.bib", "w", encoding="utf-8") as f:
        f.write(writer.write(db))

    # Build YAML blocks
    authors_yaml = "\n".join([f"  - {a}" for a in authors])

    links = []

    if doi:
        links.append(
f'''  - name: DOI
    url: "https://doi.org/{doi}"'''
        )

    if url:
        links.append(
f'''  - name: URL
    url: "{url}"'''
        )

    if eprint:
        links.append(
f'''  - name: arXiv
    url: "https://arxiv.org/abs/{eprint}"'''
        )

    links_yaml = "\n".join(links) if links else "  []"

    # Write index.md
    md = f"""---
title: "{title}"

authors:
{authors_yaml}

date: "{year}-01-01T00:00:00Z"
publishDate: "{year}-01-01T00:00:00Z"

publication_types: ["article-journal"]
publication: "{journal}"

abstract: |
{yaml_block(abstract, indent=2)}

featured: false

links:
{links_yaml}

image:
  focal_point: ""
  preview_only: false

projects: []

---
"""

    with open(folder / "index.md", "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Created {folder}")