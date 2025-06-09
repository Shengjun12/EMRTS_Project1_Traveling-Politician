import json
import math
import random

# ========== STEP 1: Load and prepare data ==========

with open("state_capitals_with_coords.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Patch missing data
data["Minnesota"]["latitude"] = 44.953703
data["Minnesota"]["longitude"] = -93.089958
data["Washington DC"] = {
    "capital": "Washington",
    "address": "1 First St SE, Washington, DC 20004",
    "latitude": 38.907192,
    "longitude": -77.036873
}

selected_states = [
    "Iowa",  # start
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana",
    "Washington DC"  # end
]
cities = selected_states
coords = [(float(data[s]["latitude"]), float(data[s]["longitude"])) for s in cities]

# Haversine formula
def haversine(p1, p2, R=6371):
    lat1, lon1, lat2, lon2 = map(math.radians, (*p1, *p2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

n = len(coords)
dist_matrix = [[haversine(coords[i], coords[j]) for j in range(n)] for i in range(n)]

# ========== STEP 2: Define ACO parameters ==========

alpha = 1.0
beta = 2.0
evaporation = 0.5
Q = 100
num_ants = 20
num_iterations = 100
pheromone = [[1.0 for _ in range(n)] for _ in range(n)]

# ========== STEP 3: ACO algorithm ==========

def run_aco():
    global pheromone
    best_route = None
    best_length = float('inf')

    for _ in range(num_iterations):
        routes = []
        lengths = []

        for _ in range(num_ants):
            visited = [0]  # Start at Iowa
            unvisited = list(range(1, n - 1))  # Intermediate M states
            while unvisited:
                i = visited[-1]
                probabilities = []
                for j in unvisited:
                    tau = pheromone[i][j] ** alpha
                    eta = (1 / dist_matrix[i][j]) ** beta
                    probabilities.append(tau * eta)
                total = sum(probabilities)
                probabilities = [p / total for p in probabilities]
                next_city = random.choices(unvisited, weights=probabilities, k=1)[0]
                visited.append(next_city)
                unvisited.remove(next_city)
            visited.append(n - 1)  # End at DC

            length = sum(dist_matrix[visited[i]][visited[i + 1]] for i in range(n - 1))
            routes.append(visited)
            lengths.append(length)

            if length < best_length:
                best_length = length
                best_route = visited[:]

        # Update pheromones
        for i in range(n):
            for j in range(n):
                pheromone[i][j] *= (1 - evaporation)

        for k in range(num_ants):
            for i in range(n - 1):
                a, b = routes[k][i], routes[k][i + 1]
                pheromone[a][b] += Q / lengths[k]
                pheromone[b][a] += Q / lengths[k]

    return best_route, round(best_length, 2)

# ========== STEP 4: Execute and print result ==========

best_path_indices, best_total_distance = run_aco()
best_route = [cities[i] for i in best_path_indices]

print("Best Route from Iowa to DC via M-State Capitals:\n")
for i, city in enumerate(best_route, 1):
    print(f"{i}. {city}")
print(f"Total straight-line distance: {best_total_distance} km")
