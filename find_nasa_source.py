from pathlib import Path

root = Path(".")

keywords = [
    "koshi_nasa_flood_pixels",
    "flood_class",
    "MCDWD",
    "MODIS",
    "NASA flood"
]

extensions = {".py", ".ipynb", ".txt", ".md"}

excluded = {
    ".venv_test",
    ".venv312",
    "node_modules",
    "__pycache__"
}

print("SEARCHING PROJECT FILES")
print("=" * 60)

for file in root.rglob("*"):
    if not file.is_file():
        continue

    if file.suffix.lower() not in extensions:
        continue

    if any(part in excluded for part in file.parts):
        continue

    try:
        content = file.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    matches = [
        keyword for keyword in keywords
        if keyword.lower() in content.lower()
    ]

    if matches:
        print("\nFILE:", file)
        print("MATCHES:", ", ".join(matches))

        lines = content.splitlines()

        for i, line in enumerate(lines):
            if any(k.lower() in line.lower() for k in matches):
                print(f"Line {i + 1}: {line[:250]}")