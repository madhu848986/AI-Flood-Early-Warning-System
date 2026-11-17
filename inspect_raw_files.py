from pathlib import Path

folders = [
    Path("datasets/raw"),
    Path("datasets/processed"),
    Path("GPM_3IMERGDF_07")
]

extensions = {".csv", ".h5", ".hdf5", ".nc", ".nc4", ".tif", ".tiff"}

for folder in folders:
    print("\n" + "=" * 60)
    print("FOLDER:", folder)
    print("=" * 60)

    if not folder.exists():
        print("Folder not found")
        continue

    files = [
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix.lower() in extensions
    ]

    print("Total data files:", len(files))

    for file in files[:100]:
        print(file, "|", round(file.stat().st_size / (1024 * 1024), 2), "MB")

    if len(files) > 100:
        print("Only first 100 files displayed.")