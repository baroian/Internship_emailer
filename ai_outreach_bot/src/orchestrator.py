from __future__ import annotations

import csv
from pathlib import Path

import typer

from . import paper_query, gpt_filter, email_finder, mailer
from .config import PROCESSED_DIR

app = typer.Typer()


@app.command()
def discover(labs: Path = typer.Option(..., exists=True)) -> None:
    researchers_file = PROCESSED_DIR / "researchers.csv"
    if researchers_file.exists():
        return
    rows = []
    with labs.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            lab_name = row["lab_name"]
            entries = paper_query.query_arxiv(lab_name, 5)
            filtered = gpt_filter.filter_candidates(lab_name, entries)
            for item in filtered:
                rows.append(
                    {
                        "lab": lab_name,
                        "name": item["name"],
                        "paper": item.get("title", ""),
                    }
                )
    with researchers_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["lab", "name", "paper"])
        writer.writeheader()
        writer.writerows(rows)


@app.command()
def enrich() -> None:
    researchers_file = PROCESSED_DIR / "researchers.csv"
    contacts_file = PROCESSED_DIR / "contacts.csv"
    if contacts_file.exists():
        return
    contacts = []
    with researchers_file.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            email_info = email_finder.find_email(row["name"], row["lab"].split()[-1])
            contacts.append(
                {"name": row["name"], "lab": row["lab"], "email": email_info["email"]}
            )
    with contacts_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "lab", "email"])
        writer.writeheader()
        writer.writerows(contacts)


@app.command()
def send() -> None:
    contacts_file = PROCESSED_DIR / "contacts.csv"
    log_file = PROCESSED_DIR / "mail_log.csv"
    sent = []
    with contacts_file.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            mailer.send_email(
                row["name"], row["email"], {"lab": row["lab"], "paper_title": ""}
            )
            sent.append({"name": row["name"], "email": row["email"], "status": "sent"})
    with log_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "status"])
        writer.writeheader()
        writer.writerows(sent)


if __name__ == "__main__":
    app()
