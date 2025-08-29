# security.py
import pandas as pd
import pandapower as pp

def n1_security(net, step=0.01, max_scale=2.0, include_impedances=True, loading_limit=100.0):
    """
    Incrementally increase load and run N-1 security screening using DC OPF (pp.rundcopp).
    Stops at the first step where the system becomes insecure.

    Parameters
    ----------
    net : pandapowerNet
        Your pandapower network.
    step : float
        Load increment per step (e.g., 0.01 = +1%).
    max_scale : float
        Max multiplier to try (safety cap).
    include_impedances : bool
        If True, also test outages of impedance elements (e.g., trafos modelled as impedance).
    loading_limit : float
        Loading percent threshold treated as a violation (default 100%).

    Returns
    -------
    secure_scale : float
        Last multiplier at which all N-1 contingencies remained secure.
    violations_df : pandas.DataFrame
        Violations at the first insecure step. Columns: element_type, element_index, max_loading_percent.
        Empty DataFrame if no violations up to max_scale.
    """
    # Cache base load so scaling is absolute each step (not compounding)
    base_load = net.load["p_mw"].copy()

    # Build contingency list: lines (and optionally impedances)
    contingencies = [("line", i) for i in net.line.index]
    if include_impedances and hasattr(net, "impedance") and len(net.impedance):
        contingencies += [("impedance", i) for i in net.impedance.index]

    scale = 1.0
    secure_scale = 1.0

    while scale + step <= max_scale + 1e-12:
        scale = round(scale + step, 8)  # avoid float creep
        # Absolute scaling from base profile
        net.load["p_mw"] = base_load * scale

        # Track violations at this scale across all contingencies
        violations = []

        for etype, idx in contingencies:
            # Toggle the element out
            if etype == "line":
                old_state = net.line.at[idx, "in_service"]
                net.line.at[idx, "in_service"] = False
            elif etype == "impedance":
                old_state = net.impedance.at[idx, "in_service"]
                net.impedance.at[idx, "in_service"] = False
            else:
                continue  # unknown type (shouldn't happen)

            try:
                # Run DC OPF
                pp.rundcopp(net)

                # Evaluate line loadings (post-contingency)
                if hasattr(net, "res_line") and len(net.res_line):
                    max_loading = float(net.res_line["loading_percent"].max())
                else:
                    # If results missing, consider it a failure
                    max_loading = float("inf")

                if max_loading >= loading_limit:
                    violations.append({
                        "element_type": etype,
                        "element_index": idx,
                        "max_loading_percent": max_loading
                    })

            except Exception as e:
                # Any solver failure is treated as insecurity
                violations.append({
                    "element_type": etype,
                    "element_index": idx,
                    "max_loading_percent": float("inf"),
                    "error": str(e)
                })

            finally:
                # Restore the element
                if etype == "line":
                    net.line.at[idx, "in_service"] = old_state
                elif etype == "impedance":
                    net.impedance.at[idx, "in_service"] = old_state

        # If any contingency violates, we’re at the first insecure step
        if violations:
            return secure_scale, pd.DataFrame(violations)

        # Otherwise, this step is secure
        secure_scale = scale

    # No violation up to max_scale
    return secure_scale, pd.DataFrame()
