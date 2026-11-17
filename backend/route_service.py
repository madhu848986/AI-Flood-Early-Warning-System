import utm
import math
import networkx as nx
import numpy as np

from scipy.spatial import cKDTree
from geopy.geocoders import Nominatim


# ==========================================
# CONFIGURATION
# ==========================================

GRAPH_FILE = (
    "datasets/processed/"
    "koshi_bilinear_flood_risk_road_graph.graphml"
)

LAMBDA = 10.0

geolocator = Nominatim(
    user_agent="koshi_flood_research_prototype"
)


# ==========================================
# LOAD ROAD NETWORK
# ==========================================

print("Loading road network...", flush=True)

G = nx.read_graphml(
    GRAPH_FILE,
    node_type=str
)

nodes = list(G.nodes(data=True))

node_ids = [node for node, data in nodes]

coordinates = np.array([
    [float(data["x"]), float(data["y"])]
    for node, data in nodes
])

tree = cKDTree(coordinates)


# ==========================================
# COORDINATE CONVERSION
# ==========================================

# WGS84 / UTM Zone 45N (EPSG:32645)

UTM_ZONE_NUMBER = 45
UTM_ZONE_LETTER = "N"


# ==========================================
# BUILD ROUTING GRAPHS
# ==========================================

print("Building routing graphs...", flush=True)

shortest_graph = nx.DiGraph()
flood_graph = nx.DiGraph()


def get_edge_name(u, v):
    """
    Retrieve the road name from the original OSM graph.
    """

    edge_data = G.get_edge_data(u, v)

    if not edge_data:
        return "Unnamed road"

    # MultiDiGraph returns a dictionary of keyed edges.
    if G.is_multigraph():
        edge_options = edge_data.values()
    else:
        edge_options = [edge_data]

    for data in edge_options:
        name = data.get("name")

        if name:
            if isinstance(name, list):
                return ", ".join(map(str, name))

            return str(name)

    return "Unnamed road"


for u, v, key, data in G.edges(keys=True, data=True):

    length = float(data["length_m"])
    risk = float(data["flood_probability"])

    cost = length * (1 + LAMBDA * risk)

    road_name = data.get("name", "Unnamed road")

    if isinstance(road_name, list):
        road_name = ", ".join(map(str, road_name))

    if (
        not shortest_graph.has_edge(u, v)
        or length < shortest_graph[u][v]["length"]
    ):
        shortest_graph.add_edge(
            u,
            v,
            length=length,
            risk=risk,
            name=road_name
        )

    if (
        not flood_graph.has_edge(u, v)
        or cost < flood_graph[u][v]["cost"]
    ):
        flood_graph.add_edge(
            u,
            v,
            length=length,
            risk=risk,
            cost=cost,
            name=road_name
        )


print("Routing service loaded successfully.", flush=True)


# ==========================================
# GEOCODING
# ==========================================

def find_location(place):

    result = geolocator.geocode(
        place,
        exactly_one=True,
        timeout=10,
        country_codes="np"
    )

    if result is None:
        raise ValueError(
            f"Location not found: {place}"
        )

    return result.latitude, result.longitude


# ==========================================
# FIND NEAREST ROAD JUNCTION
# ==========================================

def find_nearest_junction(latitude, longitude):

    x, y, _, _ = utm.from_latlon(
        latitude,
        longitude,
        force_zone_number=UTM_ZONE_NUMBER
    )

    distance, index = tree.query((x, y))

    return node_ids[index], float(distance)


# ==========================================
# BEARING CALCULATION
# ==========================================

def calculate_bearing(point1, point2):

    lat1 = math.radians(point1["latitude"])
    lat2 = math.radians(point2["latitude"])

    lon1 = math.radians(point1["longitude"])
    lon2 = math.radians(point2["longitude"])

    delta_lon = lon2 - lon1

    x = (
        math.sin(delta_lon) * math.cos(lat2)
    )

    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2)
        * math.cos(delta_lon)
    )

    bearing = math.degrees(
        math.atan2(x, y)
    )

    return (bearing + 360) % 360


# ==========================================
# TURN INSTRUCTION
# ==========================================

def get_turn_instruction(
    previous_bearing,
    next_bearing
):

    difference = (
        next_bearing - previous_bearing + 540
    ) % 360 - 180

    if -25 <= difference <= 25:
        return "Continue straight"

    if 25 < difference < 155:
        return "Turn right"

    if -155 < difference < -25:
        return "Turn left"

    return "Make a U-turn"


# ==========================================
# GENERATE NAVIGATION INSTRUCTIONS
# ==========================================

def generate_navigation_steps(
    path,
    route_coordinates,
    graph
):

    steps = []

    if len(path) < 2:

        return [{
            "instruction": "You have reached your destination.",
            "distance_m": 0,
            "road_name": ""
        }]

    steps.append({
        "instruction": "Start your journey",
        "distance_m": 0,
        "road_name": graph[path[0]][path[1]].get(
            "name",
            "Unnamed road"
        )
    })

    accumulated_distance = 0

    for i in range(1, len(path)):

        u = path[i - 1]
        v = path[i]

        edge = graph[u][v]

        accumulated_distance += float(
            edge["length"]
        )

        # Check whether the current junction is a turn.
        if i < len(path) - 1:

            previous_point = route_coordinates[i - 1]
            current_point = route_coordinates[i]
            next_point = route_coordinates[i + 1]

            incoming_bearing = calculate_bearing(
                previous_point,
                current_point
            )

            outgoing_bearing = calculate_bearing(
                current_point,
                next_point
            )

            instruction = get_turn_instruction(
                incoming_bearing,
                outgoing_bearing
            )

            # Add instructions for actual turns.
            if instruction != "Continue straight":

                next_road_name = graph[path[i]][path[i + 1]].get(
                    "name",
                    "Unnamed road"
                )

                steps.append({
                    "instruction": instruction,
                    "distance_m": round(
                        accumulated_distance,
                        2
                    ),
                    "road_name": next_road_name,
                    "latitude": current_point["latitude"],
                    "longitude": current_point["longitude"]
                })

                accumulated_distance = 0

    steps.append({
        "instruction": "You have reached your destination.",
        "distance_m": 0,
        "road_name": "",
        "latitude": route_coordinates[-1]["latitude"],
        "longitude": route_coordinates[-1]["longitude"]
    })

    return steps


# ==========================================
# CALCULATE ROUTE
# ==========================================

def calculate_route(
    graph,
    source,
    target,
    weight
):

    path = nx.shortest_path(
        graph,
        source,
        target,
        weight=weight
    )

    total_distance = 0
    weighted_risk = 0

    route_coordinates = []

    # Convert road junctions into latitude/longitude.
    for node in path:

        x = float(G.nodes[node]["x"])
        y = float(G.nodes[node]["y"])

        lat, lon = utm.to_latlon(
            x,
            y,
            UTM_ZONE_NUMBER,
            UTM_ZONE_LETTER
        )

        route_coordinates.append({
            "latitude": lat,
            "longitude": lon
        })

    # Calculate distance and flood risk.
    for u, v in zip(path[:-1], path[1:]):

        edge = graph[u][v]

        length = float(edge["length"])
        risk = float(edge["risk"])

        total_distance += length

        weighted_risk += length * risk

    average_risk = (
        weighted_risk / total_distance
        if total_distance > 0
        else 0
    )

    # Generate navigation instructions.
    navigation_steps = generate_navigation_steps(
        path,
        route_coordinates,
        graph
    )

    return {
        "distance_km": round(
            total_distance / 1000,
            3
        ),

        "estimated_risk": round(
            average_risk,
            5
        ),

        "junction_count": len(path),

        "coordinates": route_coordinates,

        "navigation_steps": navigation_steps
    }


# ==========================================
# MAIN ROUTE COMPARISON
# ==========================================

def get_route_comparison(
    start_place,
    end_place
):

    # Geocode starting point.
    start_lat, start_lon = find_location(
        start_place
    )

    # Geocode destination.
    end_lat, end_lon = find_location(
        end_place
    )

    # Find nearest road junctions.
    source, source_distance = find_nearest_junction(
        start_lat,
        start_lon
    )

    target, target_distance = find_nearest_junction(
        end_lat,
        end_lon
    )

    if source == target:
        raise ValueError(
            "Starting location and destination are too close "
            "or map to the same road junction."
        )

    if not nx.has_path(
        shortest_graph,
        source,
        target
    ):

        raise ValueError(
            "No road route is available between these locations."
        )

    # Calculate shortest-distance route.
    shortest_route = calculate_route(
        shortest_graph,
        source,
        target,
        "length"
    )

    # Calculate flood-aware route.
    flood_route = calculate_route(
        flood_graph,
        source,
        target,
        "cost"
    )

    return {

        "start_location": start_place,

        "destination": end_place,

        "shortest_route": shortest_route,

        "flood_aware_route": flood_route,

        "lambda_value": LAMBDA,

        "snapping_distance": {

            "start_metres": round(
                source_distance,
                2
            ),

            "destination_metres": round(
                target_distance,
                2
            )
        },

        "warning": (
            "Experimental route estimates based on historical "
            "flood-risk data. These routes are not verified "
            "safe evacuation routes. Follow official emergency "
            "instructions."
        )
    }