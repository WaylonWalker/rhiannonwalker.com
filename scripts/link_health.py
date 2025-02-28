#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "typer",
#     "sqlite-utils",
#     "beautifulsoup4",
#     "requests",
#     "lxml",
# ]
# ///

from bs4 import BeautifulSoup
import os
import requests
import sqlite3
import typer
from urllib.parse import urljoin

app = typer.Typer()

DB_PATH = "links.db"
ROOT_SITE = os.getenv("ROOT_SITE", "https://waylonwalker.com")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            source_file TEXT,
            status_code INTEGER,
            response_time FLOAT,
            cloudflare_cache BOOLEAN,
            content_type TEXT,
            content_disposition TEXT,
            content_length INTEGER,
            final_url TEXT,
            redirect_chain_count INTEGER,
            load_time FLOAT,
            nofollow BOOLEAN,
            canonical_url TEXT,
            canonical_mismatch BOOLEAN,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def extract_links_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        soup = BeautifulSoup(
            content, "xml" if content.lstrip().startswith("<?xml") else "lxml"
        )
        links = [a["href"] for a in soup.find_all("a", href=True)]
        return links


def scan_directory(directory: str):
    typer.echo(f"Scanning directory: {directory}")
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html") or file.endswith(".htm"):
                file_path = os.path.join(root, file)
                links = extract_links_from_html(file_path)
                for link in links:
                    cursor.execute(
                        "INSERT OR IGNORE INTO links (url, source_file) VALUES (?, ?)",
                        (link, file_path),
                    )

    conn.commit()
    conn.close()
    typer.echo("Scanning completed.")


def check_links():
    typer.echo("Checking link statuses...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT url FROM links WHERE status_code IS NULL")
    rows = cursor.fetchall()

    for (url,) in rows:
        try:
            response = requests.get(url, allow_redirects=True, timeout=5)
            status_code = response.status_code
            response_time = response.elapsed.total_seconds()
            cloudflare_cache = "cf-cache-status" in response.headers
            content_type = response.headers.get("Content-Type")
            content_disposition = response.headers.get("Content-Disposition")
            content_length = response.headers.get("Content-Length")
            final_url = response.url
            redirect_chain_count = len(response.history)
            load_time = response.elapsed.total_seconds()
            nofollow = "nofollow" in response.text
            soup = BeautifulSoup(response.text, "lxml")
            canonical = soup.find("link", rel="canonical")
            canonical_url = canonical["href"] if canonical else None
            canonical_mismatch = canonical_url and canonical_url != url
        except requests.RequestException:
            status_code = 0
            response_time = None
            cloudflare_cache = None
            content_type = None
            content_disposition = None
            content_length = None
            final_url = None
            redirect_chain_count = None
            load_time = None
            nofollow = None
            canonical_url = None
            canonical_mismatch = None

        cursor.execute(
            """
            UPDATE links 
            SET status_code = ?, response_time = ?, cloudflare_cache = ?, content_type = ?,
                content_disposition = ?, content_length = ?, final_url = ?,
                redirect_chain_count = ?, load_time = ?, nofollow = ?,
                canonical_url = ?, canonical_mismatch = ?
            WHERE url = ?
        """,
            (
                status_code,
                response_time,
                cloudflare_cache,
                content_type,
                content_disposition,
                content_length,
                final_url,
                redirect_chain_count,
                load_time,
                nofollow,
                canonical_url,
                canonical_mismatch,
                url,
            ),
        )
        conn.commit()

    conn.close()
    typer.echo("Link checking completed.")


def generate_report():
    typer.echo("Generating report...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT url, source_file, status_code, content_type, final_url, canonical_url, canonical_mismatch FROM links"
    )
    rows = cursor.fetchall()

    report = "URL | Source File | Status Code | Content Type | Final URL | Canonical URL | Canonical Mismatch\n"
    report += "-" * 120 + "\n"
    for (
        url,
        source_file,
        status_code,
        content_type,
        final_url,
        canonical_url,
        canonical_mismatch,
    ) in rows:
        report += f"{url} | {source_file} | {status_code} | {content_type or 'N/A'} | {final_url or 'N/A'} | {canonical_url or 'N/A'} | {canonical_mismatch}\n"

    conn.close()
    report_path = "link_report.txt"
    with open(report_path, "w") as f:
        f.write(report)

    typer.echo(f"Report saved to {report_path}")


@app.command()
def scan(directory: str):
    """Scan a directory for links and store them in the database."""
    scan_directory(directory)


@app.command()
def check():
    """Check the health of stored links."""
    check_links()


@app.command()
def report():
    """Generate a report from the database."""
    generate_report()


def generate_actionable_report():
    typer.echo("Generating actionable report...")
    fixes = fix_relative_links()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT url, source_file, status_code, final_url, canonical_url, canonical_mismatch
        FROM links
        WHERE status_code != 200 OR canonical_mismatch = 1
    """)
    rows = cursor.fetchall()

    report = "URL | Source File | Status Code | Final URL | Canonical URL | Canonical Mismatch\n"
    report += "-" * 100 + "\n"
    for (
        url,
        source_file,
        status_code,
        final_url,
        canonical_url,
        canonical_mismatch,
    ) in rows:
        report += f"{url} | {source_file} | {status_code} | {final_url or 'N/A'} | {canonical_url or 'N/A'} | {canonical_mismatch}\n"

    if fixes:
        report += "\nSuggested Fixes:\n"
        report += "-" * 50 + "\n"
        for old, new in fixes:
            report += f"Replace {old} with {new}\n"

    conn.close()
    report_path = "actionable_fixes_report.txt"
    with open(report_path, "w") as f:
        f.write(report)

    typer.echo(f"Actionable report saved to {report_path}")


@app.command()
def actionable():
    """Generate a report of actionable fixes."""
    generate_actionable_report()


def fix_relative_links():
    typer.echo("Fixing relative links...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM links WHERE url LIKE '/%'")
    rows = cursor.fetchall()

    fixes = []
    for (url,) in rows:
        fixed_url = urljoin(ROOT_SITE, url)
        cursor.execute("UPDATE links SET url = ? WHERE url = ?", (fixed_url, url))
        fixes.append((url, fixed_url))

    conn.commit()
    conn.close()
    return fixes


@app.command()
def fix():
    """Generate a report of actionable fixes."""
    fix_relative_links()


def migrate_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(links)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    required_columns = {
        "final_url",
        "redirect_chain_count",
        "load_time",
        "nofollow",
        "canonical_url",
        "canonical_mismatch",
    }

    missing_columns = required_columns - existing_columns

    for column in missing_columns:
        if column == "final_url":
            cursor.execute("ALTER TABLE links ADD COLUMN final_url TEXT")
        elif column == "redirect_chain_count":
            cursor.execute("ALTER TABLE links ADD COLUMN redirect_chain_count INTEGER")
        elif column == "load_time":
            cursor.execute("ALTER TABLE links ADD COLUMN load_time FLOAT")
        elif column == "nofollow":
            cursor.execute("ALTER TABLE links ADD COLUMN nofollow BOOLEAN")
        elif column == "canonical_url":
            cursor.execute("ALTER TABLE links ADD COLUMN canonical_url TEXT")
        elif column == "canonical_mismatch":
            cursor.execute("ALTER TABLE links ADD COLUMN canonical_mismatch BOOLEAN")

    conn.commit()
    conn.close()
    typer.echo("Database schema updated.")


if __name__ == "__main__":
    migrate_db()
    app()
