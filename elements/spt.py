import pandapower as pp

def create_spt_assets(net, SPT_BUS, total_SHE_load, total_SPT_load):
    
    SPT_LOAD = total_SHE_load + total_SPT_load
    
    OFTO_GEN = 4388.4

    SPT_GEN = {
    "CCGT": 1200,
    "CHP": 120,
    "Battery Storage": 97.95,
    "Hydro": 951.4,
    "Nuclear": 1270,
    "Pumped Storage": 740,
    "Wind": 8154.6
    }

    fixed_costs = {
        "Wind": 10,
        "Solar PV": 15,
        "Nuclear": 20,
        "Hydro": 40,
        "Pumped Storage": 65,
        "CCGT": 50,
        "OCGT": 60,
        "CHP": 90,
        "Oil": 55,
        "Biomass": 35,
        "Other": 70,
        "Coal": 80,
        "Battery Storage": 65
    }

 
    # Slack Bus
    EXT_GRID = pp.create_ext_grid(net, SPT_BUS, vm_pu=1, name="SPT BUS") 
    net.ext_grid.at[EXT_GRID, "max_p_mw"] = 0  # max import
    net.ext_grid.at[EXT_GRID, "min_p_mw"] = 0
  

    # SPT load creation
    pp.create_load(net, SPT_BUS, p_mw=SPT_LOAD, controllable=False)

    # offshore wind generation
    OFTO = pp.create_gen(net, SPT_BUS, p_mw=OFTO_GEN, min_p_mw=0.0, max_p_mw=OFTO_GEN, name="Wind", controllable=False)
    pp.create_poly_cost(net, element=OFTO, et="gen", cp1_eur_per_mw=10)

    for gen_type, capacity_mw in SPT_GEN.items():
        pp.create_gen(
            net,
            SPT_BUS,
            p_mw=0,
            min_p_mw=0,
            max_p_mw=capacity_mw,
            vm_pu=1.0,
            name=gen_type,
            controllable=True
        )
        
        # Add cost to OPF 
        pp.create_poly_cost(
            net,
            element=len(net.gen) - 1,
            et="gen",
            cp1_eur_per_mw=fixed_costs[gen_type]  
        )

    print(SPT_LOAD, "SPT LOAD")


    
