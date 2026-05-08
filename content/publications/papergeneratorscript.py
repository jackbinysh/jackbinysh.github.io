from pathlib import Path
import re
import textwrap
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import author


BIB_FILE = "mypapers.bib"
OUT_DIR = Path(".")
OVERWRITE = False


def slugify(text):
    text = text.replace("{", "").replace("}", "")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def clean(text):
    return text.replace("{", "").replace("}", "").replace("\n", " ").strip()


def parse_authors(entry):
    record = author(dict(entry))
    authors = []

    for a in record.get("author", []):
        first = " ".join(a.first())
        last = " ".join(a.last())
        name = f"{first} {last}".strip()
        authors.append(name)

    return authors


def yaml_list(items, indent=0):
    pad = " " * indent
    return "\n".join(f"{pad}- {item}" for item in items)


with open(BIB_FILE, encoding="utf-8") as f:
    bib = bibtexparser.load(f)


for entry in bib.entries[0:2]:
    title = clean(entry.get("title", "Untitled"))
    year = entry.get("year", "1900")
    journal = clean(entry.get("journal") or entry.get("booktitle", ""))
    abstract = clean(entry.get("abstract", ""))
    doi = clean(entry.get("doi", ""))
    url = clean(entry.get("url", ""))
    eprint = clean(entry.get("eprint", ""))

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

    links = []
    if doi:
        links.append(f'  - name: DOI\n    url: "https://doi.org/{doi}"')
    if url:
        links.append(f'  - name: URL\n    url: "{url}"')
    if eprint:
        links.append(f'  - name: arXiv\n    url: "https://arxiv.org/abs/{eprint}"')

    links_yaml = "\n".join(links) if links else "[]"

    md = textwrap.dedent(f"""\
    ---
    title: "{title}"
    authors:
    {yaml_list(authors)}

    date: "{year}-01-01T00:00:00Z"
    publishDate: "{year}-01-01T00:00:00Z"

    publication_types: ["article-journal"]
    publication: "{journal}"

    abstract: "{abstract}"

    featured: false

    links:
    {links_yaml}

    image:
      focal_point: ""
      preview_only: false

    projects: []
    ---

    """)

    with open(folder / "index.md", "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Created {folder}")