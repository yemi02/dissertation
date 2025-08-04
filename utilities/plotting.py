import pandapower.topology as top
import networkx as nx
import matplotlib.pyplot as plt
from network import net

# Network topology
# Create the graph from the pandapower network
G = top.create_nxgraph(net, respect_switches=True)

# Use spring layout with tuned spacing (k increases spacing between nodes)
pos = nx.spring_layout(G, k=4.0, iterations=300, seed=42)

# Color nodes by type: green = generator, orange = load, lightblue = regular bus
node_colors = []
for node in G.nodes:
    if node in net.gen.bus.values:
        node_colors.append("green")
    elif node in net.load.bus.values:
        node_colors.append("orange")
    else:
        node_colors.append("lightblue")

# Optional: Label a few key buses (e.g., ext_grid or largest gen)
labels = {}
for node in G.nodes:
    if node in net.ext_grid.bus.values or node in net.gen.bus.value_counts().head(5).index:
        labels[node] = f"Bus {node}"

# Plotting
plt.figure(figsize=(24, 20))  # Large canvas
nx.draw_networkx_nodes(G, pos,
                       node_color=node_colors,
                       node_size=80,
                       alpha=0.9)
nx.draw_networkx_edges(G, pos,
                       edge_color="gray",
                       alpha=0.5,
                       width=1)
nx.draw_networkx_labels(G, pos, labels,
                        font_size=8,
                        font_color="black")

plt.title("PandaPower Network Topology (Well-Spaced, High Detail)", fontsize=18)
plt.axis("off")
plt.tight_layout()

# Save high-resolution image
plt.savefig("national_grid_topology.png", dpi=400)
plt.show()








