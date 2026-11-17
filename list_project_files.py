
import os

project_path = r"C:\Users\HEMA\Flood-Early-Warning"

for root, dirs, files in os.walk(project_path):
    dirs[:] = [
        d for d in dirs
        if d not in [".ipynb_checkpoints", "__pycache__", ".git"]
    ]

    print("\nFolder:", root)

    for file in files:
        print("  File:", file)
