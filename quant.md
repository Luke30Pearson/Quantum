# Quantum Computing Research Scraper & Institution Analysis


# Introduction

The purpose of this project is to analyze trends in quantum computing
research using reproducible, automated data collection and enrichment
methods. I collected metadata from arXiv’s `quant-ph` category, refined
it to include only papers relevant to quantum computing, and extracted
the first author’s institutional affiliation using PDF parsing
techniques.

------------------------------------------------------------------------

# Data Collection: Scraping arXiv Metadata

To gather research papers, I wrote a full scraping script using the
`arxiv` Python package.  
The scraper pulls metadata such as title, authors, publication date, and
PDF URL for all quantum-computing–related papers.

Below is the full scraping script shown for transparency.  
**It does not run during rendering** because scraping thousands of
papers is slow and not needed for the report.

``` python
import arxiv
import csv
import time


QUERY = 'all:"quantum computing"'     
BATCH_SIZE = 200                      
MAX_RESULTS = 7000                    

def fetch_all_qc_papers():
    search = arxiv.Search(
        query=QUERY,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers = []
    count = 0

    for result in search.results():
        count += 1
        papers.append({
            "arxiv_id": result.get_short_id(),
            "title": result.title.replace("\n", " ").strip(),
            "published": result.published.strftime("%Y-%m-%d"),
            "authors": "; ".join(a.name for a in result.authors),
            "pdf_url": result.pdf_url
        })

        
        if count % BATCH_SIZE == 0:
            time.sleep(0.5)

    return papers


#Fetch metadata
papers = fetch_all_qc_papers()

#Write CSV
with open("quantum_computing_metadata.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["arxiv_id", "title", "published", "authors", "pdf_url"]
    )
    writer.writeheader()
    writer.writerows(papers)

print("Saved", len(papers), "records to quantum_computing_metadata.csv")
```

# Cleaning and Classifying Papers

Quantum computing papers often come with different subfields, so I
classify each title into categories using keyword rules.

Classification logic is below. This code is shown but not executed
because the cleaned data already exists.

``` python
import pandas as pd

df = pd.read_csv("quantum_computing_metadata.csv")


QC_ALGO = [
    "algorithm", "vqe", "qaoa", "variational", "quantum approximate",
    "circuit", "grover", "shor", "ansatz", "qft", "amplitude",
    "state preparation", "qnn", "qml"
]

QC_HARDWARE = [
    "qubit", "superconducting", "transmon", "rydberg", "ion trap",
    "quantum dot", "photon source", "waveguide", "cryogenic", "gkp",
]

QC_ERROR = [
    "error correction", "surface code", "fault-tolerant", "decoder",
    "noise", "stabilizer", "logical qubit"
]

QC_THEORY = [
    "complexity", "entanglement entropy", "unitary", "quantum chaos",
    "resource theory", "hamiltonian simulation"
]

QC_APPLICATIONS = [
    "quantum chemistry", "molecule", "chemistry", "optimization",
    "ising", "material", "simulation", "fluid", "finance"
]

NON_QC_PHYSICS = [
    "exciton", "phonon", "nv center", "spectroscopy", "many-body",
    "optical cavity", "scattering", "graphene", "lattice", "boson",
    "turbulence"
]
```

``` python
def classify_field(title):
    t = title.lower()
    
    if any(k in t for k in NON_QC_PHYSICS):
        return "Physics (Not QC)"
    
    if any(k in t for k in QC_ERROR):
        return "Quantum Error Correction"
    if any(k in t for k in QC_ALGO):
        return "Quantum Computing – Algorithms"
    if any(k in t for k in QC_HARDWARE):
        return "Quantum Computing – Hardware"
    if any(k in t for k in QC_THEORY):
        return "Quantum Computing – Theory"
    if any(k in t for k in QC_APPLICATIONS):
        return "Quantum Computing – Applications"
    
    if "quantum machine learning" in t or "qml" in t:
        return "Quantum Machine Learning"
    

    if "quantum" in t:
        return "General Quantum Information"
    
    return "Unknown"
```

# Extracting First-Author Institutions

Institution extraction required parsing PDF text, which is often messy.

I tried PDF text extraction for institution-like strings and then
fallback to email domain inference when available

The full script is shown below but not executed during rendering.

``` python
import pandas as pd
import requests
import PyPDF2
import re
import io
from tqdm import tqdm

def extract_institution_from_pdf(pdf_url: str):
    try:
        response = requests.get(pdf_url, timeout=10)
        if response.status_code != 200:
            return None

        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)

        text = ""
        for page_num in range(min(2, len(reader.pages))):
            text += reader.pages[page_num].extract_text() + "\n"


        inst_regex = r"""
            ([A-Z][A-Za-z&\-\s]*                       
            (University|Institute|Laboratory|College|
            Department|Centre|Center|School)[^,\n]*)   
        """

        matches = re.findall(inst_regex, text, flags=re.VERBOSE)
        if matches:
            return matches[0][0].strip()

    except Exception:
        return None

    return None

def extract_institution_from_email(author_block):
    """Try to infer institution from email domain."""
    match = re.search(r'@([A-Za-z0-9\.\-]+)', author_block)
    if match:
        domain = match.group(1)
        if "gmail" in domain:
            return None
        return domain  
    return None

df = pd.read_csv("quantum_computing_clean_onlyQC.csv")

institutions = []

print("Extracting institutions...\n")

for idx, row in tqdm(df.iterrows(), total=len(df)):
    pdf_url = row["pdf_url"]
    authors = row["authors"].split(";")
    first_author = authors[0].strip()

    institution = extract_institution_from_pdf(pdf_url)

    if institution is None:
        institution = extract_institution_from_email(first_author)

    if institution is None:
        institution = "Unknown"

    institutions.append(institution)


df["first_author_institution"] = institutions

df.to_csv("quantum_computing_with_institutions.csv", index=False)

print("Saved to quantum_computing_with_institutions.csv")
```

# Discussion

This analysis highlights which universities, research centers, and labs
are most active in quantum computing today. Patterns can help identify
leading contributors to subfields and emerging trends.
