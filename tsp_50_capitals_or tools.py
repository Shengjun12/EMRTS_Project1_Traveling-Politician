"""
tsp_50_capitals.py
------------------------------------------------------------
Find the shortest great-circle path that starts in Des Moines,
visits every U.S. state capital once, and ends in Washington DC
using Google OR-Tools.
------------------------------------------------------------
"""

import json, math, os
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# -----------------------------------------------------------
# 1. LOAD  LAT / LON  DATA  ---------------------------------
# -----------------------------------------------------------
JSON_FILE = "state_capitals_with_coords.json"
if not os.path.exists(JSON_FILE):
    raise FileNotFoundError(f"{JSON_FILE} not found in current directory")

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Patch any coordinates you know are missing -------------
MISSING = {
    # "State": {"latitude": 12.345, "longitude": -98.765},
    "Minnesota": {"latitude": 44.953703, "longitude": -93.089958},
    "New York":  {"latitude": 42.652579, "longitude": -73.756232},
    "Ohio":      {"latitude": 39.961176, "longitude": -82.998794},
    "Tennessee": {"latitude": 36.162663, "longitude": -86.781601},
}
data.update(MISSING)

# --- Add Washington DC (end node but not a state) -----------
data["Washington DC"] = {
    "capital":   "Washington",
    "address":   "1 First St SE, Washington, DC 20004",
    "latitude":  38.907192,
    "longitude": -77.036873
}

# -----------------------------------------------------------
# 2.  BUILD ORDERED CITY LIST  -------------------------------
# -----------------------------------------------------------
START_STATE = "Iowa"           # index 0
END_CITY    = "Washington DC"  # last index

# put Iowa first, DC last, all others alphabetical in between
other_states = sorted(s for s in data if s not in {START_STATE, END_CITY})
ordered_states = [START_STATE] + other_states + [END_CITY]

coords = [
    (float(data[s]["latitude"]), float(data[s]["longitude"]))
    for s in ordered_states
]

# -----------------------------------------------------------
# 3.  HAVERSINE DISTANCE MATRIX  -----------------------------
# -----------------------------------------------------------
def haversine(p1, p2, R=6371.0):
    """great-circle distance (km)"""
    lat1, lon1, lat2, lon2 = map(math.radians, (*p1, *p2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2) ** 2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2) ** 2
    return R * 2 * math.asin(math.sqrt(a))

N = len(coords)
dist_km = [[haversine(coords[i], coords[j]) for j in range(N)] for i in range(N)]
# OR-Tools likes integer costs → convert km to meters and round
dist_m  = [[int(d * 1000) for d in row] for row in dist_km]

# -----------------------------------------------------------
# 4.  OR-TOOLS  TSP  WITH  FIXED  START / END  ---------------
# -----------------------------------------------------------
manager = pywrapcp.RoutingIndexManager(
    N,               # number of nodes
    1,               # one “vehicle” (politician)
    [0],             # start index list   (Iowa)
    [N - 1]          # end   index list   (Washington DC)
)
routing = pywrapcp.RoutingModel(manager)

def distance_cb(i, j):
    return dist_m[manager.IndexToNode(i)][manager.IndexToNode(j)]

transit_cb = routing.RegisterTransitCallback(distance_cb)
routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

# search parameters
params = pywrapcp.DefaultRoutingSearchParameters()
params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
params.time_limit.seconds = 20          # adjust if you want longer search
params.log_search = False

solution = routing.SolveWithParameters(params)
if not solution:
    raise RuntimeError("No solution found – increase time limit?")

# -----------------------------------------------------------
# 5.  EXTRACT AND PRINT ROUTE  -------------------------------
# -----------------------------------------------------------
index = routing.Start(0)
route, total_m = [], 0
while not routing.IsEnd(index):
    node = manager.IndexToNode(index)
    route.append(ordered_states[node])
    nxt  = solution.Value(routing.NextVar(index))
    total_m += dist_m[node][manager.IndexToNode(nxt)]
    index = nxt
route.append(ordered_states[manager.IndexToNode(index)])

print("\n--- Optimal Route (OR-Tools) ---")
for i, city in enumerate(route, 1):
    print(f"{i:2d}. {city}")
print(f"\nTotal straight-line distance : {total_m/1000:,.2f} km")