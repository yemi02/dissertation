import pandapower.topology as ppt
import pandapower as pp
import warnings

warnings.filterwarnings('ignore')

def run_dcopf(net):
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

    # Ensure we still have a slack or generators
    if net.ext_grid.empty and net.gen.empty:
        raise ValueError("No slack/ext_grid or generator in the largest island; cannot run power flow.")

    # --- Run DC Power Flow ---
    pp.rundcpp(net)
    print('DCPF converged:', net.converged)

    # --- Run DC Optimal Power Flow ---
    try:
        pp.rundcopp(net)
        print('DCOPF converged:', net.OPF_converged)
    except Exception as e:
        print('DCOPF failed to converge')
        print('Error:', e)

    return net
