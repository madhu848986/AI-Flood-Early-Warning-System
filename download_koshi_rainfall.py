
import earthaccess
import os

output_folder = os.path.join(
    "datasets", "raw", "gpm_historical"
)
os.makedirs(output_folder, exist_ok=True)

print("Logging in to NASA Earthdata...")
earthaccess.login(strategy="interactive")

print("Searching for daily rainfall data...")
granules = earthaccess.search_data(
    short_name="GPM_3IMERGDF",
    version="07",
    temporal=("2020-09-08", "2020-09-30"),
    bounding_box=(85, 25, 89.5, 29.5),
    count=100
)

print("Granules found:", len(granules))

if granules:
    files = earthaccess.download(
        granules,
        output_folder
    )
    print("Download process finished.")
    print("Files returned:", len(files))
else:
    print("No granules found. Check the dataset search.")
