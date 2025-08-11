import pandapower as pp
import warnings

from elements.buses import create_buses
from elements.lines import create_lines
from elements.transformers import create_transformers
from elements.loads import create_loads, group_bus_by_substation
from elements.generators import create_gens
from elements.interconnectors import create_interconnectors
from elements.spt import create_spt_assets
from utilities.run_dc import run_dcopf 
from tests.generation_summary import generation_summary
from tests.get_results import get_results

warnings.filterwarnings('ignore')

# --- Create Empty Network ---
net = pp.create_empty_network()

# --- Create Elements ---
SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup = create_buses(net)
create_lines(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)
create_transformers(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)
substation_group = group_bus_by_substation(NGET_bus_lookup)
total_SHE_load, total_SPT_load = create_loads(net, NGET_bus_lookup, substation_group)
create_gens(net, NGET_bus_lookup, substation_group)
create_interconnectors(net, NGET_bus_lookup, mode="import")

create_spt_assets(net, SPT_BUS, total_SHE_load, total_SPT_load)

EXT_GRID = pp.create_ext_grid(net, SPT_BUS, vm_pu=1, name="SPT BUS")
net.ext_grid.at[EXT_GRID, "max_p_mw"] = 0  # max import
net.ext_grid.at[EXT_GRID, "min_p_mw"] = 0

# Apply load scaling
net.load.loc[:, 'p_mw'] 

# Apply max angle difference
# net.line["max_angle_diff_degree"] = 15

# Run DCPF and DCOPF
run_dcopf(net)

# Get network results and DCOPF results
get_results(net)

# Generation summary
generation_summary(net)

