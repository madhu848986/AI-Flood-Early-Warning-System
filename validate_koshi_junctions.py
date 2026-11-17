import sqlite3
import csv
import shapely

junction_db = sqlite3.connect(
    "datasets/processed/koshi_unique_road_junctions.gpkg"
)

road_db = sqlite3.connect(
    "datasets/processed/koshi_vehicle_roads_grade.gpkg"
)

junctions = junction_db.execute(
    "SELECT junction_id, road_indices, geom "
    "FROM koshi_unique_road_junctions "
    "ORDER BY junction_id LIMIT 100"
).fetchall()

results = []

for junction_id, road_indices, geometry in junctions:

    point = shapely.from_wkb(geometry[8:])

    references = road_indices.split(",")

    for reference in references:

        road_fid = int(reference) + 1

        road_geometry = road_db.execute(
            "SELECT geom FROM koshi_vehicle_roads_grade WHERE fid = ?",
            (road_fid,)
        ).fetchone()

        if road_geometry is None:
            continue

        data = road_geometry[0]
        envelope = (data[3] >> 1) & 7

        offset = 8

        if envelope == 1:
            offset += 32
        elif envelope in (2, 3):
            offset += 48
        elif envelope == 4:
            offset += 64

        line = shapely.from_wkb(data[offset:])

        distance = point.distance(line)

        results.append([
            junction_id,
            road_fid,
            round(distance, 4)
        ])

with open(
    "datasets/processed/koshi_junction_validation_100.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "junction_id",
        "road_fid",
        "distance_m"
    ])

    writer.writerows(results)

distances = [row[2] for row in results]

print("JUNCTIONS TESTED:", len(junctions))
print("ROAD CONNECTIONS TESTED:", len(results))

if distances:
    print("MAXIMUM DISTANCE:", max(distances), "m")
    print("MATCHES WITHIN 0.1 m:", sum(d <= 0.1 for d in distances))
    print("MATCHES WITHIN 1 m:", sum(d <= 1 for d in distances))
    print("MATCHES WITHIN 5 m:", sum(d <= 5 for d in distances))

junction_db.close()
road_db.close()