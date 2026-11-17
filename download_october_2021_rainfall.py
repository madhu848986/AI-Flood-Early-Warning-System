
import earthaccess
import os

output_folder = os.path.join(
    "datasets", "raw", "gpm_historical", "october_2021"
)

os.makedirs(output_folder, exist_ok=True)

print("Logging in to NASA Earthdata...")
earthaccess.login(strategy="interactive")

print("Searching for daily rainfall data...")
granules = earthaccess.search_data(
    short_name="GPM_3IMERGDF",
    version="07",
    temporal=("2021-10-13", "2021-10-14"),
    bounding_box=(85, 25, 89.5, 29.5),
    count=100
)

print("Granules found:", len(granules))

if granules:
    print("Downloading rainfall files...")

    files = earthaccess.download(
        granules,
        output_folder
    )

    print("Download process finished.")
    print("Files returned:", len(files))
    print("Output folder:", output_folder)

    print("\nDownloaded files:")
    for file_path in files:
        print(file_path)

else:
    print("No granules found.")
    print("Check the dataset name, dates, and Earthdata access.")
