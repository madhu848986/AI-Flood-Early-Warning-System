
import os

folder = os.path.join("datasets", "raw", "elevation")

# Tile rows and columns covering the selected rectangle
latitudes = range(25, 30)
longitudes = range(85, 90)

available = {
    filename.removesuffix(".hgt")
    for filename in os.listdir(folder)
    if filename.lower().endswith(".hgt")
}

print("ELEVATION TILE COVERAGE")
print("-" * 40)

missing = []

for lat in latitudes:
    for lon in longitudes:
        tile = f"N{lat:02d}E{lon:03d}"

        if tile in available:
            print(tile, "- AVAILABLE")
        else:
            print(tile, "- MISSING")
            missing.append(tile)

print("\nAvailable tiles:", 25 - len(missing))
print("Missing tiles:", len(missing))

if missing:
    print("\nTiles to locate:")
    for tile in missing:
        print(tile + ".hgt")
