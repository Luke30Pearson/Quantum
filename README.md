# Quantum Computing Research Scraper & Institution Mapping

This repository contains a complete workflow for tracking emerging research in quantum computing using automated scraping, metadata cleaning, and institution extraction. The goal of this project is to identify which institutions, labs, and authors are most active and what type of research is emerging in quantum computing to understand the landscape.

---

## Project Overview

The pipeline performs three major tasks:

### **1. Incremental ArXiv Scraping**
- Queries the *quant-ph* category for papers related to quantum computing  
- Extracts metadata 
- Appends only new papers to a growing CSV dataset   

Files:
- `quant.qmd`
- `scrape_incremental.py`
- `quantum_computing_metadata.csv`
- `last_scrape.txt`

### **2. Institution Extraction**
Extracts the first author’s institutional affiliation by:
- Reading each paper’s PDF
- Parsing the first-page header text  
- Using pattern recognition / regex to identify institutional strings  
- Creating a fully enriched dataset

Files:
- `quant.qmd`
- `quantum_computing_with_institutions.csv`

### **3. Quarto Report**
A fully documented analysis in `quant.qmd` that includes:
- Project explanation  
- Description of methods  
- Code snippets using chunk options (echo, eval, results, etc.)  
- Tables, plots, and insights about active institutions  
- Clean, reproducible GitHub Markdown output  

---


| File | Description |
|------|-------------|
| `quant.qmd` | Full written report and executable analysis (Quarto). Includes the institution-extraction code. |
| `scrape_incremental.py` | Script for continuously pulling new quantum computing papers from arXiv. |
| `quantum_computing_metadata.csv` | Raw scraped metadata collected by the incremental scraper. |
| `quantum_computing_clean_onlyQC.csv` | Cleaned dataset before institution extraction. |
| `quantum_computing_with_institutions.csv` | Final enriched dataset with institution column added. |
| `last_scrape.txt` | Tracks the most recent arXiv scrape date. |





