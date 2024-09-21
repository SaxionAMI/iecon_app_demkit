

def iecon_parse_spb_data_2_demkit(spb_data:dict) -> dict:
    """
        Convert an IECON device data message to DEMKIT data format for InfluxDB
    Args:
        spb_data:   spB Message dictionary
                    Example: {'timestamp': '1726920058818', 'metrics': [{'name': 'ENE_CNT_EXP', 'timestamp': '1726920056000', 'datatype': 10, 'doubleValue': 2732.902, 'value': 2732.902}], 'seq': '120'}

    Returns: Dictionary with converted values.

    """

    out = dict()    # return data

    # Convert the data fields
    metrics = spb_data.get("metrics", dict())

    for metric in metrics:

        name = metric["name"]
        value = metric["value"]

        if name == "POW":
            out["W-power.P"] = value
        elif name == "POW_L1":
            out["W-power.L1"] = value     # TODO check if the name is correct for a phase power
        elif name == "POW_L2":
            out["W-power.L2"] = value
        elif name == "POW_L3":
            out["W-power.L3"] = value

        elif name == "POW_APP":
            out["VA-power.S"] = value
        elif name == "POW_REAC":
            out["VAR-power.Q"] = value

        elif name == "POW_FACT":
            out["PF-powerfactor.PF"] = value

        elif name == "CURR":
            out["A-current.A"] = value
        elif name == "CURR_L1":
            out["A-current.L1"] = value
        elif name == "CURR_L2":
            out["A-current.L2"] = value
        elif name == "CURR_L3":
            out["A-current.L3"] = value

        elif name == "VOLT":
            out["V-voltage.V"] = value
        elif name == "VOLT_L1":
            out["V-voltage.L1N"] = value
        elif name == "VOLT_L2":
            out["V-voltage.L2N"] = value
        elif name == "VOLT_L3":
            out["V-voltage.L3N"] = value
        elif name == "VOLT_L1L2":
            out["V-voltage.L1L2"] = value
        elif name == "VOLT_L2L3":
            out["V-voltage.L2L3"] = value
        elif name == "VOLT_L3L1":
            out["V-voltage.L3L1"] = value

        elif name == "FREQ":
            out["H-frequency.AC"] = value

        # TODO Implement this values, what are the names in Demkit?
        elif name == "ENE_CNT_EXP":
            pass
        elif name == "ENE_CNT_EXP_L1":
            pass
        elif name == "ENE_CNT_EXP_L2":
            pass
        elif name == "ENE_CNT_EXP_L3":
            pass
        elif name == "ENE_CNT_IMP":
            pass
        elif name == "ENE_CNT_IMP_L1":
            pass
        elif name == "ENE_CNT_IMP_L2":
            pass
        elif name == "ENE_CNT_IMP_L3":
            pass
        elif name == "ENE_CNT_REAC_EXP":
            pass

        else:
            print("Unknown demkit data name for iecon field name: " + name)
            pass

    return out
