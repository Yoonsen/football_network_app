import json
import numpy as np
import networkx as nx
from itertools import combinations
import os

def cosine_similarity(v1, v2):
    dot = np.dot(v1, v2)
    norm = np.linalg.norm(v1) * np.linalg.norm(v2)
    return dot / norm if norm > 0 else 0

def build_dataset(input_file, output_file, threshold=0.15):
    with open(input_file, "r") as f:
        data = json.load(f)

    all_clubs = set()
    for nation, clubs in data.items():
        all_clubs.update(clubs.keys())
        
    if "Unattached" in all_clubs: all_clubs.remove("Unattached")
    if "Free agent" in all_clubs: all_clubs.remove("Free agent")
    
    all_clubs = list(all_clubs)
    
    vectors = {}
    for nation, clubs in data.items():
        vec = np.zeros(len(all_clubs))
        for i, club in enumerate(all_clubs):
            vec[i] = clubs.get(club, 0)
        vectors[nation] = vec

    G = nx.Graph()
    G.add_nodes_from(data.keys())
        
    all_edges = []
    for n1, n2 in combinations(data.keys(), 2):
        sim = cosine_similarity(vectors[n1], vectors[n2])
        if sim > 0:
            shared = set(data[n1].keys()).intersection(set(data[n2].keys()))
            shared -= {"Unattached", "Free agent"}
            shared_details = []
            for c in shared:
                cnt = min(data[n1][c], data[n2][c])
                shared_details.append({"club": c, "count": cnt})
            
            all_edges.append({
                "from": n1,
                "to": n2,
                "weight": float(sim),
                "shared": shared_details
            })
            
            # Legger til edges over terskel til G for å beregne klynger
            if sim >= threshold:
                G.add_edge(n1, n2, weight=sim)

    from networkx.algorithms.community import louvain_communities
    centrality = nx.betweenness_centrality(G)
    
    if len(G.edges()) > 0:
        communities = louvain_communities(G, seed=42)
    else:
        communities = [{n} for n in G.nodes()]
        
    nodes = []
    for node in data.keys():
        # Finn klynge
        group = 0
        for i, comm in enumerate(communities):
            if node in comm:
                group = i
                break
                
        # Topp 5 klubber
        top_clubs = sorted(
            data[node].items(), 
            key=lambda x: (x[1], x[0] not in ["Unattached", "Free agent"]), 
            reverse=True
        )[:5]
        
        nodes.append({
            "id": node,
            "label": node,
            "group": group,
            "betweenness": centrality.get(node, 0),
            "top_clubs": [{"club": c, "count": cnt} for c, cnt in top_clubs]
        })

    output_data = {
        "nodes": nodes,
        "edges": all_edges
    }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Bygget {output_file} med {len(nodes)} noder og {len(all_edges)} totale kanter.")

if __name__ == "__main__":
    build_dataset("data_2022.json", "public/graph_2022.json")
    build_dataset("data_2026.json", "public/graph_2026.json")
