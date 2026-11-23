"""
Mini-Courier Planner
Design & Analysis of Algorithms (ETCCDA302)

Algorithms:
1. Merge Sort: prioritize parcels by priority score, then earliest deadline.
2. 0/1 Knapsack (Dynamic Programming): choose the most valuable feasible parcel set.
3. Dijkstra: shortest paths in a weighted, undirected road graph.
4. Nearest Neighbor TSP approximation: create a delivery visit order and return to depot.

Run:
    python main.py
    python main.py --data data/sample_data.json
    python main.py --benchmark

All distances are illustrative distance units and all parcel values are illustrative.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any


def merge_sort_parcels(parcels: List[dict]) -> List[dict]:
    """Stable merge sort: higher priority first, then earlier deadline."""
    if len(parcels) <= 1:
        return parcels[:]
    mid = len(parcels) // 2
    left = merge_sort_parcels(parcels[:mid])
    right = merge_sort_parcels(parcels[mid:])

    def key(p):
        return (-p["priority"], p["deadline"])

    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def knapsack_01(parcels: List[dict], capacity: int) -> Tuple[List[dict], int]:
    """Return selected parcels and maximum total value using 0/1 DP."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        weight, value = parcels[i-1]["weight"], parcels[i-1]["value"]
        for cap in range(capacity + 1):
            dp[i][cap] = dp[i-1][cap]
            if weight <= cap:
                dp[i][cap] = max(dp[i][cap], value + dp[i-1][cap-weight])

    selected = []
    cap = capacity
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i-1][cap]:
            selected.append(parcels[i-1])
            cap -= parcels[i-1]["weight"]
    selected.reverse()
    return selected, dp[n][capacity]


def build_graph(nodes: List[str], roads: List[dict]) -> Dict[str, List[Tuple[str, float]]]:
    graph = {node: [] for node in nodes}
    for road in roads:
        a, b, distance = road["from"], road["to"], float(road["distance"])
        if distance < 0:
            raise ValueError("Dijkstra requires non-negative edge weights.")
        if a not in graph or b not in graph:
            raise ValueError(f"Road references unknown node: {a} or {b}")
        graph[a].append((b, distance))
        graph[b].append((a, distance))
    return graph


def dijkstra(graph: Dict[str, List[Tuple[str, float]]], source: str):
    """Return distance and predecessor maps using a simple O(V^2 + E) implementation."""
    if source not in graph:
        raise ValueError(f"Unknown source node: {source}")
    unvisited = set(graph)
    dist = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    dist[source] = 0.0

    while unvisited:
        current = min(unvisited, key=lambda node: dist[node])
        if dist[current] == float("inf"):
            break
        unvisited.remove(current)
        for neighbor, weight in graph[current]:
            if neighbor in unvisited and dist[current] + weight < dist[neighbor]:
                dist[neighbor] = dist[current] + weight
                previous[neighbor] = current
    return dist, previous


def reconstruct_path(previous: dict, target: str) -> List[str]:
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = previous[current]
    return list(reversed(path))


def shortest_path(graph, source: str, target: str):
    distances, previous = dijkstra(graph, source)
    if distances[target] == float("inf"):
        return [], float("inf")
    return reconstruct_path(previous, target), distances[target]


def nearest_neighbor_tsp(graph, depot: str, delivery_nodes: List[str]):
    """Greedy TSP approximation using shortest-path distances between stops."""
    remaining = set(delivery_nodes)
    remaining.discard(depot)
    current = depot
    visit_order = [depot]
    total = 0.0
    legs = []

    while remaining:
        distances, previous = dijkstra(graph, current)
        reachable = [node for node in remaining if distances[node] < float("inf")]
        if not reachable:
            raise ValueError("Some delivery points are unreachable from the current route.")
        next_node = min(reachable, key=lambda node: (distances[node], node))
        leg_path = reconstruct_path(previous, next_node)
        leg_distance = distances[next_node]
        legs.append({"from": current, "to": next_node, "path": leg_path, "distance": leg_distance})
        total += leg_distance
        current = next_node
        visit_order.append(current)
        remaining.remove(current)

    if current != depot:
        distances, previous = dijkstra(graph, current)
        if distances[depot] == float("inf"):
            raise ValueError("Depot is unreachable from the final delivery point.")
        leg_path = reconstruct_path(previous, depot)
        legs.append({"from": current, "to": depot, "path": leg_path, "distance": distances[depot]})
        total += distances[depot]
        visit_order.append(depot)

    return visit_order, legs, total


def load_data(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    required = {"depot", "capacity", "parcels", "nodes", "roads"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Dataset is missing fields: {sorted(missing)}")
    return data


def run_planner(data: dict, verbose=True) -> dict:
    t0 = time.perf_counter()
    sorted_parcels = merge_sort_parcels(data["parcels"])
    sort_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    selected, total_value = knapsack_01(sorted_parcels, int(data["capacity"]))
    knapsack_time = time.perf_counter() - t0

    graph = build_graph(data["nodes"], data["roads"])
    destinations = sorted({p["destination"] for p in selected})
    unknown = set(destinations) - set(graph)
    if unknown:
        raise ValueError(f"Parcel destinations missing from graph: {sorted(unknown)}")

    t0 = time.perf_counter()
    route, legs, route_distance = nearest_neighbor_tsp(graph, data["depot"], destinations)
    route_time = time.perf_counter() - t0

    result = {
        "sorted_parcels": sorted_parcels,
        "selected_parcels": selected,
        "total_weight": sum(p["weight"] for p in selected),
        "capacity": data["capacity"],
        "total_value": total_value,
        "route": route,
        "legs": legs,
        "route_distance": route_distance,
        "timings_seconds": {
            "merge_sort": sort_time,
            "knapsack_dp": knapsack_time,
            "route_planning": route_time
        }
    }
    if verbose:
        print_report(result, data)
    return result


def print_report(result: dict, data: dict):
    print("\n" + "=" * 66)
    print("                 MINI-COURIER PLANNER")
    print("=" * 66)
    print(f"Depot: {data['depot']} | Bag capacity: {data['capacity']} kg")
    print("\n1) PARCEL PRIORITIZATION (Merge Sort)")
    for p in result["sorted_parcels"]:
        print(f"  {p['id']:>4} | {p['name']:<18} | priority={p['priority']} "
              f"| deadline={p['deadline']} | {p['weight']} kg | value={p['value']}")
    print("\n2) OPTIMAL PACKING (0/1 Knapsack DP)")
    if result["selected_parcels"]:
        for p in result["selected_parcels"]:
            print(f"  - {p['id']}: {p['name']} -> {p['destination']} "
                  f"({p['weight']} kg, value {p['value']})")
    else:
        print("  No parcels fit the capacity.")
    print(f"  Packed weight: {result['total_weight']} / {result['capacity']} kg")
    print(f"  Maximum total value: {result['total_value']}")
    print("\n3) DELIVERY ROUTE (Dijkstra + Nearest Neighbor TSP)")
    print("  Visit order: " + " -> ".join(result["route"]))
    for leg in result["legs"]:
        print(f"  {leg['from']} -> {leg['to']}: {' -> '.join(leg['path'])} "
              f"({leg['distance']:.1f} units)")
    print(f"  Total route distance (including return): {result['route_distance']:.1f} units")
    print("\n4) MEASURED EXECUTION TIMES")
    for name, seconds in result["timings_seconds"].items():
        print(f"  {name:<18}: {seconds:.8f} seconds")
    print("=" * 66)


def benchmark():
    """Benchmark core algorithms on increasing synthetic input sizes."""
    rng = __import__("random").Random(42)
    sizes = [20, 50, 100, 200, 400]
    records = []
    for n in sizes:
        parcels = [{
            "id": f"P{i}", "name": f"Parcel {i}", "priority": rng.randint(1, 5),
            "deadline": rng.randint(1, 30), "weight": rng.randint(1, 10),
            "value": rng.randint(10, 100), "destination": "N1"
        } for i in range(n)]
        t0 = time.perf_counter(); merge_sort_parcels(parcels); sort_s = time.perf_counter()-t0
        t0 = time.perf_counter(); knapsack_01(parcels, 100); dp_s = time.perf_counter()-t0
        records.append({"input_size": n, "merge_sort_seconds": sort_s, "knapsack_dp_seconds": dp_s})
    out = Path("results")
    out.mkdir(exist_ok=True)
    with (out / "benchmark_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = __import__("csv").DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader(); writer.writerows(records)
    print("\nBenchmark results")
    print("n\tMerge Sort (s)\tKnapsack DP (s)")
    for r in records:
        print(f"{r['input_size']}\t{r['merge_sort_seconds']:.8f}\t{r['knapsack_dp_seconds']:.8f}")
    print("\nSaved: results/benchmark_results.csv")


def main():
    parser = argparse.ArgumentParser(description="Mini-Courier Planner")
    parser.add_argument("--data", default="data/sample_data.json", help="Path to JSON dataset")
    parser.add_argument("--benchmark", action="store_true", help="Run increasing-size performance tests")
    args = parser.parse_args()
    if args.benchmark:
        benchmark()
    else:
        data = load_data(Path(args.data))
        result = run_planner(data)
        Path("results").mkdir(exist_ok=True)
        with open("results/latest_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print("\nSaved detailed result to results/latest_result.json")


if __name__ == "__main__":
    main()
