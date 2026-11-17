
from pathlib import Path
import earthaccess

output_dir = Path("datasets/raw/gpm_historical/october_2021")
output_dir.mkdir(parents=True, exist_ok=True)

print("Sign in with your NASA Earthdata account...")
auth = earthaccess.login(strategy="interactive")

if not auth.authenticated:
    raise SystemExit("Earthdata login failed. Check your login and archive authorization.")

print("Searching for IMERG daily files...")

results = earthaccess.search_data(
    short_name="GPM_3IMERGDF",
    version="07",
    temporal=("2021-10-06", "2021-10-12"),
)

print("Granules found:", len(results))

if not results:
    raise SystemExit(
        "No files found. We need to verify the collection and version."
    )

downloaded = earthaccess.download(results, str(output_dir))
print("Download results:", len(downloaded))
print("Finished.")
