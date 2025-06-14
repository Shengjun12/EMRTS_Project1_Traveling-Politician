# Traveling Politician: U.S. State Capitals TSP Solver

This project solves a version of the **Traveling Salesman Problem (TSP)** that finds the shortest route starting in **Des Moines, Iowa**, visiting **all 50 U.S. state capitals**, and ending in **Washington, D.C.** using **Google OR-Tools**.

 Route is computed using straight-line (great-circle) distances between capitals based on latitude and longitude coordinates.

---

##  Project Structure

- `tsp_50_capitals_or_tools.py`: Main Python script using OR-Tools to compute optimal TSP route.
- `state_capitals_with_coords.json`: Input file containing capital names, addresses, and geolocation (latitude, longitude).
- Output: A printed list of capitals in the optimal visiting order and the total distance.

---

## Features

- Calculates great-circle distances using the Haversine formula.
- Patches missing or incorrect coordinates for a few capitals.
- Models the problem with **fixed start** (Iowa) and **fixed end** (Washington, D.C.).
-  Uses Google OR-Tools with:
  - `PATH_CHEAPEST_ARC` initialization
  - `GUIDED_LOCAL_SEARCH` optimization
-  Customizable time limit for solution search.

---

##  How to Run

### Requirements
- Python 3.7+
- [Google OR-Tools](https://developers.google.com/optimization)

### Install dependencies
```bash
pip install ortools
