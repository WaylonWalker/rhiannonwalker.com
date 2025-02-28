from datetime import datetime, timedelta
import os
from pathlib import Path

OBSIDIAN_VAULT_PATH = "."
OUTPUT_FILE = "Recent-Posts.md"


def get_recent_files(vault_path, days=7):
    recent_files = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)

    for root, _, files in os.walk(vault_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                if mtime >= cutoff_date:
                    relative_path = os.path.relpath(file_path, vault_path)
                    recent_files.append((relative_path, mtime))

    return sorted(recent_files, key=lambda x: x[1], reverse=True)


def generate_markdown(recent_files):
    lines = ["# Recent Posts\n"]
    for file, mtime in recent_files:
        lines.append(
            f'- [[{Path(file).stem}]] (Modified: {mtime.strftime("%Y-%m-%d %H:%M:%S")})'
        )
    return "\n".join(lines)


def main():
    recent_files = get_recent_files(OBSIDIAN_VAULT_PATH)
    markdown_content = generate_markdown(recent_files)

    with open(os.path.join(OBSIDIAN_VAULT_PATH, OUTPUT_FILE), "w") as f:
        f.write(markdown_content)


if __name__ == "__main__":
    main()
