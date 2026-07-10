import networkx as nx
import threading

def run():
    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4])
    G.add_edge(1, 2)
    # Disconnected graph
    print("Computing layout...")
    pos = nx.spring_layout(G)
    print("Done!")

t = threading.Thread(target=run)
t.start()
t.join()
