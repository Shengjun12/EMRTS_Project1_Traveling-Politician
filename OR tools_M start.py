import json
import math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# === STEP 1: Load coordinates ===
with open("state_capitals_with_coords.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data["Minnesota"]["latitude"] = 44.953703
data["Minnesota"]["longitude"] = -93.089958
data["Washington DC"] = {
    "capital": "Washington",
    "address": "1 First St SE, Washington, DC 20004",
    "latitude": 38.907192,
    "longitude": -77.036873
}

selected_states = [
    "Iowa", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Washington DC"
]
cities = selected_states
coords = [(float(data[s]["latitude"]), float(data[s]["longitude"])) for s in cities]

# === STEP 2: Distance Matrix ===
def haversine(p1, p2, R=6371):
    lat1, lon1, lat2, lon2 = map(math.radians, (*p1, *p2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

dist_matrix = [[int(haversine(a, b) * 1000) for b in coords] for a in coords]

# === STEP 3: OR-Tools Routing ===
manager = pywrapcp.RoutingIndexManager(len(dist_matrix), 1, [0], [len(cities) - 1])
routing = pywrapcp.RoutingModel(manager)

def distance_callback(i, j):
    return dist_matrix[manager.IndexToNode(i)][manager.IndexToNode(j)]

transit_cb_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_index)

params = pywrapcp.DefaultRoutingSearchParameters()
params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
params.time_limit.seconds = 10

solution = routing.SolveWithParameters(params)

# === STEP 4: Output Result ===
if solution:
    index = routing.Start(0)
    route = []
    total_distance = 0
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        route.append(cities[node_index])
        next_index = solution.Value(routing.NextVar(index))
        total_distance += dist_matrix[node_index][manager.IndexToNode(next_index)]
        index = next_index
    route.append(cities[manager.IndexToNode(index)])
    print("\nOptimal Route:")
    for i, city in enumerate(route, 1):
        print(f"{i}. {city}")
    print(f"\nTotal Distance: {round(total_distance / 1000, 2)} km")
else:
    print("No solution found.")
