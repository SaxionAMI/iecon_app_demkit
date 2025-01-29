from mqtt_spb_wrapper import MqttSpbEntityScada


def iecon_eon_find_eond_by_attr (eon : MqttSpbEntityScada.EdgeEntity, eond_attributes:dict) -> str:
    """
    Search for a EoND Device within an EoN entity for a given attributes

    Args:
        eon: EoN entity
        eond_attributes:    Search attributes

    Returns: EoND entity or None if not found.
    """

    # Missing method on spb wrapper 2.0.1 version, to be fixed in next versions
    # devices = eon.search_device_by_attribute(attributes=eond_attributes)

    devices = []  # List of devices found

    # Iterate over the devices
    for eond, device in eon.entities_eond.items():

        is_found = True  # Flag to mark a detection

        # Iterate over the attributes to be found
        for k, v in eond_attributes.items():

            # not found on previous iteration/attribute, then exit
            if not is_found:
                break

            # Search for attribute name
            if k not in device.attributes.get_names():
                is_found = False
                continue  # Not found

            # Compare the attribute value
            if not str(device.attributes.get_value(k)) == str(v):
                is_found = False
                continue

        # If found a match, add the device
        if is_found:
            devices.append(eond)

    # Select the device
    entity = None
    if len(devices) == 0:
        return entity
    elif len(devices) == 1:
        entity = devices[0]
    elif len(devices) > 1:      # NOTE If more entities are found, we select the first one
        entity = devices[0]

    return entity

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
            out["W-power.L1"] = value
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
        elif name == "POW_FACT_L1":
            out["PF-powerfactor.L1"] = value
        elif name == "POW_FACT_L2":
            out["PF-powerfactor.L2"] = value
        elif name == "POW_FACT_L3":
            out["PF-powerfactor.L3"] = value

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

        # Implement this values, what are the names in Demkit?
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
        elif name == "ENE_CNT_REAC_EXP_L1":
            pass
        elif name == "ENE_CNT_REAC_EXP_L2":
            pass
        elif name == "ENE_CNT_REAC_EXP_L3":
            pass

        elif name == "ENE_CNT_REAC_IMP":
            pass
        elif name == "ENE_CNT_REAC_IMP_L1":
            pass
        elif name == "ENE_CNT_REAC_IMP_L2":
            pass
        elif name == "ENE_CNT_REAC_IMP_L3":
            pass


        elif name == "ENER_CNT_IMP":
            pass
        elif name == "ENER_CNT_EXP":
            pass

        elif name == "POW_APP_L1":
            pass
        elif name == "POW_APP_L2":
            pass
        elif name == "POW_APP_L3":
            pass

        elif name == "POW_REAC_L1":
            pass
        elif name == "POW_REAC_L2":
            pass
        elif name == "POW_REAC_L3":
            pass

        elif name == "CURR_Neutral":
            pass

        elif name == "ENE_CNT_REAC_EXP_L1":
            pass
        elif name == "ENE_CNT_REAC_EXP_L2":
            pass
        elif name == "ENE_CNT_REAC_EXP_L3":
            pass

        else:
            print("Unknown demkit data name for iecon field name: " + name)
            pass

    return out
