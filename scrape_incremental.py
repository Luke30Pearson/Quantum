import arxiv
import csv
import os
from datetime import datetime

CSV_FILE = "quantum_computing_metadata.csv"
LAST_SCRAPE_FILE = "last_scrape.txt"

QUERY_BASE = 'cat:quant-ph AND ("quantum computing" OR "quantum computer" OR qubit OR "quantum circuit" OR "quantum algorithm")'
MAX_RESULTS = 5000     


def load_last_scrape_date():
    """Read last scrape date from file or return None."""
    if not os.path.exists(LAST_SCRAPE_FILE):
        return None
        
    with open(LAST_SCRAPE_FILE, "r") as f:
        text = f.read().strip()
        return datetime.strptime(text, "%Y-%m-%d")


def save_last_scrape_date(date_obj):
    """Save the newest paper date to file."""
    with open(LAST_SCRAPE_FILE, "w") as f:
        f.write(date_obj.strftime("%Y-%m-%d"))


def fetch_new_papers(since_date):
    """Pull papers newer than the last scrape."""
    print(f"Fetching papers newer than {since_date.strftime('%Y-%m-%d')}...\n")

    search = arxiv.Search(
        query=QUERY_BASE,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    new_rows = []
    newest_date_found = since_date

    for result in search.results():
        pub_date = result.published.replace(tzinfo=None)

        if pub_date <= since_date:
            continue   

        new_rows.append({
            "arxiv_id": result.get_short_id(),
            "title": result.title.replace("\n", " ").strip(),
            "published": pub_date.strftime("%Y-%m-%d"),
            "authors": "; ".join(a.name for a in result.authors),
            "pdf_url": result.pdf_url
        })

        if pub_date > newest_date_found:
            newest_date_found = pub_date

    print(f"Found {len(new_rows)} new papers.")
    return new_rows, newest_date_found


def append_to_csv(rows):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["arxiv_id", "title", "published", "authors", "pdf_url"]
        )
        
        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)


def run_incremental_scrape():
    last_date = load_last_scrape_date()

    if last_date is None:
        print("No last_scrape.txt found — running full scrape first.")
        last_date = datetime(1900, 1, 1)

    new_rows, newest_date = fetch_new_papers(last_date)

    if len(new_rows) > 0:
        append_to_csv(new_rows)
        save_last_scrape_date(newest_date)
        print(f"Updated CSV with {len(new_rows)} new papers.")
        print(f" Updated last_scrape.txt → {newest_date.strftime('%Y-%m-%d')}\n")
    else:
        print("No new papers since last scrape.\n")


if __name__ == "__main__":
    run_incremental_scrape()
