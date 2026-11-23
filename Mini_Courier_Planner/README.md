# Mini-Courier Planner

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**Institution:** K.R. Mangalam University  
**Language:** Python 3

## Overview
This project simulates a courier service. It prioritizes parcels, selects a feasible high-value set for one trip, and plans a delivery tour through a weighted road network.

## Algorithms used
1. **Merge Sort** — sorts parcels by descending priority; ties are resolved by earlier deadline. Time: `O(n log n)`, auxiliary space: `O(n)`.
2. **0/1 Knapsack Dynamic Programming** — chooses parcels maximizing total value without exceeding bag capacity. Time: `O(nW)`, space: `O(nW)`, where `W` is capacity.
3. **Dijkstra's Algorithm** — finds shortest paths on a non-negative weighted graph. This implementation uses a simple unvisited-set scan: `O(V^2 + E)` time and `O(V)` auxiliary space (excluding graph storage).
4. **Nearest Neighbor TSP Approximation** — repeatedly visits the closest unvisited delivery point using shortest-path distances, then returns to depot. It is a heuristic and does not guarantee the optimal TSP tour.

## Requirements
- Python 3.9+
- No third-party packages are required to run the planner.

## Run
Open a terminal in this folder:
```bash
python main.py
```
Use a different dataset:
```bash
python main.py --data data/small_data.json
python main.py --data data/large_data.json
```
Run performance tests:
```bash
python main.py --benchmark
```

## Dataset format
- `depot`: starting/ending node.
- `capacity`: maximum total parcel weight.
- `nodes`: graph vertices.
- `roads`: undirected edges with non-negative `distance`.
- `parcels`: parcel ID, name, priority, deadline, weight, value and destination.

Distances are illustrative units; parcel values and weights are sample data for academic demonstration.

## Project structure
```text
Mini_Courier_Planner/
├── main.py
├── README.md
├── requirements.txt
├── data/
│   ├── sample_data.json
│   ├── small_data.json
│   └── large_data.json
├── docs/
│   └── Capstone_Report.docx
└── results/
    ├── benchmark_results.csv
    ├── benchmark_runtime.png
    └── sample_output.txt
```

## Important design note
Sorting determines the priority display order. Knapsack independently maximizes total parcel value under the weight constraint; therefore the final selected set is not necessarily the first items in the sorted list. The route is calculated for the unique destinations of selected parcels. The route uses shortest-path distances between stops and returns to the depot.

## Limitations and future improvements
- Nearest Neighbor is an approximation, not an exact TSP solver.
- The graph is static; live traffic and road closures are not modelled.
- Knapsack uses integer weights and capacity.
- Future work could use a priority queue for Dijkstra, time-window constraints, live map data, and 2-opt route improvement.
