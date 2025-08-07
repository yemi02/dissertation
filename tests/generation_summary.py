# gen_summary.py

def generation_summary(net):
    gen_types = [
    "Wind",
    "Solar PV",
    "Nuclear",
    "Hydro",
    "Pumped Storage",
    "CCGT",
    "OCGT",
    "Biomass",
    "Other",
    "Coal",
    "Battery Storage",
    "BritNed",
    "East-West",
    "Nemo Link",
    "IFA-2",
    "IFA",
    "North Sea Link",
    "ElecLink",
    "Viking Link",
    "Greenlink"
    ]

    total_generation_mw = net.res_gen['p_mw'].sum() + net.res_ext_grid["p_mw"].sum()
    total_load_mw = net.res_load["p_mw"].sum() 
    generation_by_type = {gen_type: 0.0 for gen_type in gen_types}
    generation_by_type['Unknown'] = 0.0

    for idx, gen in net.gen.iterrows():
        gen_name = gen['name']
        gen_output = net.res_gen.at[idx, 'p_mw']

        matched_type = None
        for gen_type in gen_types:
            if gen_type.lower() in gen_name.lower():
                matched_type = gen_type
                break
        
        if matched_type:
            generation_by_type[matched_type] += gen_output
        else:
            generation_by_type['Unknown'] += gen_output

    print(f"Total load in network: {total_load_mw:.2f} MW")
    print(f"Total generation in network: {total_generation_mw:.2f} MW")
    print("Generation by type:")
    for gen_type, total in generation_by_type.items():
        print(f"  {gen_type}: {total:.2f} MW")

    
