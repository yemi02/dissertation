import pandapower as pp
import math

def convert_mva_to_ka(mva_rating):
    return ((mva_rating * 1_000_000) / ( math.sqrt(3) * 400_000)) / 1000

# add scaling factor for the function.

def create_interconnectors(net, NGET_bus_lookup, mode="import"):
    # Define buses    
    france_1 = pp.create_bus(net, vn_kv=400, name="France")
    france_2 = pp.create_bus(net, vn_kv=400, name="France")
    france_3 = pp.create_bus(net, vn_kv=400, name="France")
    netherlands = pp.create_bus(net, vn_kv=400, name="Netherlands")
    belgium = pp.create_bus(net, vn_kv=400, name="Belgium")
    norway = pp.create_bus(net, vn_kv=400, name="Norway")
    denmark = pp.create_bus(net, vn_kv=400, name="Denmark")
    ireland_1 = pp.create_bus(net, vn_kv=400, name="Ireland")    
    ireland_2 = pp.create_bus(net, vn_kv=400, name="Ireland")    

    interconnectors = {
    "IFA": {
        "capacity_mw": 2000,
        "from_bus": "SELL",
        "to_bus": france_1,
        "length_km": 73,
        "mode": "import",
        "mw_flow": 1800  
    },
    "BritNed": {
        "capacity_mw": 1000,
        "from_bus": "GRAI",
        "to_bus": netherlands,
        "length_km": 260,
        "mode": "import",
        "mw_flow": 400
    },
    "East-West": {
        "capacity_mw": 500,
        "from_bus": "FLIB",
        "to_bus": ireland_1,
        "length_km": 261,
        "mode": "import",
        "mw_flow": 0
    },
    "Nemo Link": {
        "capacity_mw": 1000,
        "from_bus": "RICH",
        "to_bus": belgium,
        "length_km": 140,
        "mode": "import",
        "mw_flow": 520
    },
    "IFA-2": {
        "capacity_mw": 1000,
        "from_bus": "CHIL",
        "to_bus": france_2,
        "length_km": 204,
        "mode": "import",
        "mw_flow": 910
    },
    "North Sea Link": {
        "capacity_mw": 1400,
        "from_bus": "BLYT",
        "to_bus": norway,
        "length_km": 720,
        "mode": "import",
        "mw_flow": 924
    },
    "ElecLink": {
        "capacity_mw": 1000,
        "from_bus": "SELL",
        "to_bus": france_3,
        "length_km": 51,
        "mode": "import",
        "mw_flow": 996
    },
    "Viking Link": {
        "capacity_mw": 1400,
        "from_bus": "BICF",
        "to_bus": denmark,
        "length_km": 765,
        "mode": "import",
        "mw_flow": 382
    },
    "Greenlink": {
        "capacity_mw": 500,
        "from_bus": "PEMB",
        "to_bus": ireland_2,
        "length_km": 190,
        "mode": "import",
        "mw_flow": 0
    },
    }
    
    for name, data in interconnectors.items():
        bus_name = data["to_bus"]
        max_p_mw = data["capacity_mw"]

        if mode == "import":
            # Interconnector acts as a generator importing power to your network
            pp.create_gen(net, bus=bus_name, p_mw=0.0, min_p_mw=0.0,
                    max_p_mw=max_p_mw, vm_pu=1, name=name, controllable=True)
            pp.create_poly_cost(
                    net, element=bus_name, et='gen',
                    cp0_eur=0.0,
                    cp1_eur_per_mw=30,
                    cp2_eur_per_mw2=0.0
            )
        elif mode == "export":
            # Interconnector acts as a load exporting power from your network
            pp.create_load(net, bus=bus_name, p_mw=max_p_mw, name=name)

        elif mode == "manual":
            ic_mode = data["mode"]
            p_mw = data["mw_flow"]

            if ic_mode == "import":
                # Interconnector acts as a generator importing power to your network
                pp.create_gen(net, bus=bus_name, p_mw=p_mw, min_p_mw=0.0,
                        max_p_mw=max_p_mw, vm_pu=1, name=name, controllable=False)
                pp.create_poly_cost(
                        net, element=bus_name, et='gen',
                        cp0_eur=0.0,
                        cp1_eur_per_mw=30,
                        cp2_eur_per_mw2=0.0
                )
            elif ic_mode == "export":
                # Interconnector acts as a load exporting power from your network
                pp.create_load(net, bus=bus_name, p_mw=max_p_mw, name=name)

        else:
            raise ValueError("Invalid mode. Use 'import' or 'export'.")


    for name, data in interconnectors.items():
        sub_prefix = data["from_bus"].lower()
        matching_bus = None
        
        for key, value in NGET_bus_lookup.items():
            if key.lower().startswith(sub_prefix):
                matching_bus = value
                break

        if matching_bus is None:
            raise KeyError(f"No matching bus found for prefix {sub_prefix}")

        from_bus = matching_bus
        to_bus = data["to_bus"]
        length_km = data["length_km"]
        capacity_mw = data["capacity_mw"]
        ka_rating = convert_mva_to_ka(capacity_mw)    


        pp.create_std_type(
            net,
            {
                "c_nf_per_km": 0,    
                "r_ohm_per_km": 0, 
                "x_ohm_per_km": 0.2,  
                "max_i_ka": ka_rating,
                "g_us_per_km": 0,    
                "type": "cs"        
            },
            name=f"std_{name}",
            element="line"
        )

        pp.create_line(
            net,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=length_km, 
            std_type=f"std_{name}",  # Custom standard type 
            name="Interconnector",
            max_loading_percent=100
        )

    print("Interconnector creation complete.")
