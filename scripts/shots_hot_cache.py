#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "typer",
#     "rich",
# ]
# ///

import json
import os
import re
import requests
from rich.progress import Progress
import typer

app = typer.Typer()

MARKOUT_DIR = "markout"
LINK_PATTERN = re.compile(r"https://shots\.wayl\.one/[^\s\"\'\)]+")
LINKS_FILE = "shots-links.json"


def clean_link(link: str) -> str:
    """Remove unwanted parts from links."""
    return link.split(")](")[0].rstrip("\\")


def find_links_in_directory(directory: str) -> list[str]:
    """Search for links in all files in the given directory."""
    links = set()
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    links.update(
                        clean_link(link) for link in LINK_PATTERN.findall(content)
                    )
            except UnicodeDecodeError:
                typer.echo(f"Skipping non-text file: {file_path}")
    return list(links)


def load_existing_links() -> dict:
    """Load existing links from the JSON file."""
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_links(links: dict):
    """Save links to the JSON file."""
    with open(LINKS_FILE, "w") as f:
        json.dump(links, f, indent=2)
    typer.echo(f"Saved {len(links)} links to {LINKS_FILE}")


def check_cloudflare_cache(link: str) -> str:
    """Check if the link hits Cloudflare cache."""
    try:
        response = requests.head(link)
        cache_status = response.headers.get("cf-cache-status", "MISS")
        return cache_status
    except requests.RequestException as e:
        typer.echo(f"Failed to check link: {e}")
        return "ERROR"


@app.command()
def main(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Skip checking Cloudflare cache"
    ),
):
    """Main function to find, store, and validate links."""
    typer.echo("Scanning for links...")
    found_links = find_links_in_directory(MARKOUT_DIR)
    existing_links = load_existing_links()

    for link in found_links:
        if link not in existing_links:
            existing_links[link] = "PENDING"

    save_links(existing_links)

    if not dry_run:
        typer.echo("Checking links for Cloudflare cache...")
        with Progress() as progress:
            task = progress.add_task("Checking Links", total=len(found_links))
            for link in found_links:
                if existing_links.get(link) != "HIT":
                    existing_links[link] = check_cloudflare_cache(link)
                    save_links(existing_links)
                progress.update(task, advance=1)

    typer.echo("All links processed.")


if __name__ == "__main__":
    app()
