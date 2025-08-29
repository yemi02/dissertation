import pandas as pd
import pandapower as pp
import os


def get_results(net):
    # Ensure the results folder exists
    os.makedirs("results", exist_ok=True)

    # Save Network for reference
    pp.to_excel(net, os.path.join("results", "network.xlsx"))


    # --- Save Results ---
    with pd.ExcelWriter(os.path.join("results", "dc_opf_results_winter_scenario.xlsx")) as writer:
        net.res_bus.to_excel(writer, sheet_name="Bus Results")
        net.res_line.to_excel(writer, sheet_name="Line Results")
        net.res_gen.to_excel(writer, sheet_name="Generator Results")
        net.res_load.to_excel(writer, sheet_name="Load Results")
        net.res_ext_grid.to_excel(writer, sheet_name="External Grid Results")