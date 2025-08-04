import pandapower.topology as ppt
import pandapower as pp
import warnings

warnings.filterwarnings('ignore')

def keep_largest_island(net):
    """
    Removes all islands except the largest from the network.
    
    Parameters: net (pandapowerNet): The pandapower network object to clean up.
        
    Returns: net (pandapowerNet): The modified network containing only the largest island.
    """
    # Create the networkx graph
    graph = ppt.create_nxgraph(net)

    # Find all islands (connected components)
    islands = list(ppt.connected_components(graph))

    if not islands:
        raise ValueError("No islands found in the network.")

    # Find the largest island by bus count
    largest_island = max(islands, key=len)

    # Buses to drop = all except the largest island
    buses_to_drop = list(set(net.bus.index) - set(largest_island))

    if buses_to_drop:
        pp.drop_buses(net, buses_to_drop)

    return net
