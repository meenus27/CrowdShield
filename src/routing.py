import networkx as nx
import osmnx as ox
import os

def load_graph(online=True, center_point=(9.9312,76.2673), dist=2000):
    """
    Load graph with error handling. Returns None on failure.
    """
    try:
        if online:
            return ox.graph_from_point(center_point, dist=dist, network_type="walk")
        else:
            # fallback: load cached graph
            graph_path = "data/local_graph.graphml"
            if os.path.exists(graph_path):
                return ox.load_graphml(graph_path)
            else:
                print(f"Warning: Local graph not found at {graph_path}, creating empty graph")
                return None
    except Exception as e:
        print(f"Graph loading error: {e}")
        return None

def block_edges_by_hazards(G, hazards_gdf):
    """
    Block edges intersecting hazard polygons. Returns graph copy.
    """
    if G is None:
        return None
    if hazards_gdf is None or hazards_gdf.empty:
        return G
    try:
        G_blocked = G.copy()
        # TODO: implement hazard intersection logic
        # For now, just return a copy
        return G_blocked
    except Exception as e:
        print(f"Block edges error: {e}")
        return G

def compute_shortest_path(G, origin, target, weight="length"):
    """
    Compute shortest path. Handles errors gracefully.
    """
    if G is None:
        return None
    try:
        # Find nearest nodes if origin/target are not in graph
        origin_node = ox.nearest_nodes(G, origin[1], origin[0]) if hasattr(ox, 'nearest_nodes') else origin
        target_node = ox.nearest_nodes(G, target[1], target[0]) if hasattr(ox, 'nearest_nodes') else target
        
        path = nx.shortest_path(G, origin_node, target_node, weight=weight)
        # Convert nodes to coordinates
        if isinstance(path[0], (int, tuple)):
            coords = []
            for node in path:
                if isinstance(node, tuple):
                    coords.append(node)
                else:
                    try:
                        coords.append((G.nodes[node].get('y', origin[0]), G.nodes[node].get('x', origin[1])))
                    except:
                        coords.append(origin)
            return coords if coords else [origin, target]
        return path
    except Exception as e:
        print(f"Shortest path error: {e}")
        return None

def compute_fastest_path(G, origin, target):
    """
    Compute fastest path by travel time. Handles errors gracefully.
    """
    if G is None:
        return None
    try:
        # weight by travel time (length / speed)
        for u,v,k,data in G.edges(keys=True, data=True):
            speed = data.get("speed_kph", 30)
            if "length" in data and speed > 0:
                data["time"] = data["length"] / (speed*1000/3600)
            else:
                data["time"] = data.get("length", 100) / 10  # Default fallback
        
        origin_node = ox.nearest_nodes(G, origin[1], origin[0]) if hasattr(ox, 'nearest_nodes') else origin
        target_node = ox.nearest_nodes(G, target[1], target[0]) if hasattr(ox, 'nearest_nodes') else target
        
        path = nx.shortest_path(G, origin_node, target_node, weight="time")
        # Convert nodes to coordinates similar to shortest_path
        if isinstance(path[0], (int, tuple)):
            coords = []
            for node in path:
                if isinstance(node, tuple):
                    coords.append(node)
                else:
                    try:
                        coords.append((G.nodes[node].get('y', origin[0]), G.nodes[node].get('x', origin[1])))
                    except:
                        coords.append(origin)
            return coords if coords else [origin, target]
        return path
    except Exception as e:
        print(f"Fastest path error: {e}")
        return None

def compute_safest_path(G, origin, target, hazards=None):
    """
    Compute safest path avoiding hazards. Handles errors gracefully.
    """
    if G is None:
        return None
    try:
        # weight by hazard penalty
        for u,v,k,data in G.edges(keys=True, data=True):
            hazard_penalty = data.get("hazard_penalty", 0)
            length = data.get("length", 100)
            data["safe_weight"] = length * (1 + hazard_penalty)
        
        origin_node = ox.nearest_nodes(G, origin[1], origin[0]) if hasattr(ox, 'nearest_nodes') else origin
        target_node = ox.nearest_nodes(G, target[1], target[0]) if hasattr(ox, 'nearest_nodes') else target
        
        path = nx.shortest_path(G, origin_node, target_node, weight="safe_weight")
        # Convert nodes to coordinates
        if isinstance(path[0], (int, tuple)):
            coords = []
            for node in path:
                if isinstance(node, tuple):
                    coords.append(node)
                else:
                    try:
                        coords.append((G.nodes[node].get('y', origin[0]), G.nodes[node].get('x', origin[1])))
                    except:
                        coords.append(origin)
            return coords if coords else [origin, target]
        return path
    except Exception as e:
        print(f"Safest path error: {e}")
        return None

def grid_route_fallback(origin, target):
    # crude straight-line fallback
    return [origin, target]
