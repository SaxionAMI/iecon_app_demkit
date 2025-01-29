
# Host, required to control/coordinate the simulation itself
from hosts.liveHost import LiveHost

# ---- IECON components
from mqtt_spb_wrapper import MqttSpbEntityScada

from iecon.dev.ieconLoadDev import IeconLoadDev
from iecon.dev.ieconPvDev import IeconPvDev
from iecon.ctrl.ieconLoadCtrl import IeconLoadCtrl
from iecon.ctrl.ieconLivePvCtrl import IeconLivePvCtrl

from iecon.dev.tools.ieconDevTools import iecon_eon_find_eond_by_attr

# ---- Devices
from dev.meterDev import MeterDev  # Meter device that aggregates the load of all individual devices
from environment.sunEnv import SunEnv

# ---- Controllers
from ctrl.congestionPoint import CongestionPoint  # Import a congestion point
from ctrl.groupCtrl import GroupCtrl  # Group controller to control multiple devices, implements Profile Steering


def iecon_eon_provision_demkit_components(
        host: LiveHost,
        sun: SunEnv,
        spb_scada: MqttSpbEntityScada,
        spb_eon_name,
):
    """
    Automatic provisioning of Demkit components based on spB Edge / EoN entity name.

    spb_scada is used to search for the EoN entity, and get its device entities for Consumption,Generation and Production.
    Then virtual demkit devices will be added to the simulation

    Args:
        host:               Demkit simulation host
        spb_scada:          spB SCADA object to detect current entities
        spb_eon_name:       spB EON entity name ( House )
        sun:                Sun object for PV predictions
    """

    entities_detected = False   # Flag to mark if at least one entity was detected in the house. If not CTRL is removed

    spb_eon = spb_scada.entities_eon[spb_eon_name]  # Get the EoN object, to search over the devices

    host.logMsg("  Searching EoN <%s> for devices:" % spb_eon_name)

    # Search for CONSUMPTION
    entity_consumption = iecon_eon_find_eond_by_attr(
        eon=spb_eon,
        eond_attributes={
            'CTYPEC': "consumption",
            "CTYPE": "electricity",
        },
    )

    # Search for GENERATION
    entity_generation = iecon_eon_find_eond_by_attr(
        eon=spb_eon,
        eond_attributes={
            'CTYPEC': "generation",
            "CTYPE": "electricity",
        },
    )

    # Search for SUPPLY
    entity_supply = iecon_eon_find_eond_by_attr(
        eon=spb_eon,
        eond_attributes={
            'CTYPEC': "supply",
            "CTYPE": "electricity",
        },
    )

    # ---- DEMKIT Registration of entities ------------------------------------

    # ADDING A HEMS - add a controller if necessary
    if host.useCongestionPoints:
        cp = CongestionPoint()
        cp.setUpperLimit('ELECTRICITY', 3 * 25 * 230)  # 3 phase 25A connection ELECTRICITY limits
        cp.setLowerLimit('ELECTRICITY', -3 * 25 * 230)

    if host.useCongestionPoints:
        ctrl = GroupCtrl(spb_eon_name + "-ems-ctrl", host, None, cp)

        ctrl.log_db_measurement = spb_eon_name  # Force the data to be inserted at the DB measurement for the EoN

    else:
        ctrl = GroupCtrl(spb_eon_name + "-ems-ctrl", host, None)  # params: name, simHost
        ctrl.minImprovement = 0.01
        if host.useMultipleCommits:
            ctrl.maxIters = 4
        else:
            ctrl.maxIters = 8
        ctrl.timeBase = host.ctrlTimeBase  # 900 is advised hre, must be a multiple of the simulation timeBase
        ctrl.useEventControl = host.useEC  # Enable / disable event-based control
        ctrl.isFleetController = True  # Very important to set this right in case of large structures. The root controller

        # needs to be a fleet controller anyway. See 4.3 of Hoogsteen's thesis
        ctrl.strictComfort = not host.useIslanding
        ctrl.islanding = host.useIslanding
        ctrl.planHorizon = 2 * int(24 * 3600 / host.ctrlTimeBase)
        ctrl.planInterval = int(24 * 3600 / host.ctrlTimeBase)
        ctrl.predefinedNextPlan = host.alignplan

        # Force DB log values to be written in the EoN DB Measurement.
        ctrl.log_db_measurement = spb_eon_name  # Force the data to be inserted at the DB measurement for the EoN

    # --- HOUSE METER ( supply point at DEMKIT )
    if entity_supply:

        entities_detected = True  # Mark entity detected

        # Print some information
        host.logMsg("   Found SUPPLY entity      : " + entity_supply +
                   "\t - " + str(["%s:%s" % (str(attr["name"]), str(attr["value"])) for attr in
                                spb_eon.entities_eond[entity_supply].attributes.get_dictionary()]))

        # Virtual simulation device - This is the equivalent to the physical SUPPLY spB meter
        sm = MeterDev(name=entity_supply + "-ems-dev-virt", host=host)

    else:
        host.logWarning("   WARNING - This house doesn't have a SUPPLY entity")

    # --- CONSUMPTION ---- Add house consumption to the house
    if entity_consumption:

        entities_detected = True  # Mark entity detected

        # Print some information
        host.logMsg("   Found CONSUMPTION entity : " + entity_consumption +
                   "\t - " + str(["%s:%s" % (str(attr["name"]), str(attr["value"])) for attr in
                                spb_eon.entities_eond[entity_consumption].attributes.get_dictionary()]))

        # Device Entity
        load = IeconLoadDev(
            host=host,
            iecon_scada=spb_scada,
            eon_name=spb_eon_name,
            eond_name=entity_consumption,
            influx=True,
        )
        load.timeBase = host.timeBase  # Timebase of the dataset, not the simulation!
        load.strictComfort = not host.useIslanding
        sm.addDevice(load)

        # Controller entity
        loadctrl = IeconLoadCtrl(
            name=entity_consumption,
            dev=load,
            ctrl=ctrl,
            host=host
        )
        loadctrl.log_db_measurement = spb_eon_name  # Force DB log values to be written in the EoN DB Measurement.
        loadctrl.perfectPredictions = host.usePP  # Use perfect predictions or not
        loadctrl.useEventControl = host.useEC  # Use event-based control
        loadctrl.timeBase = host.ctrlTimeBase  # TimeBase for controllers
        loadctrl.strictComfort = not host.useIslanding
        loadctrl.islanding = host.useIslanding

    else:
        host.logWarning("   WARNING - This house doesn't have a CONSUMPTION entity")

    # --- PV ---- Solar panel based on provided data -----------------------------------------------
    if entity_generation:

        entities_detected = True    # Mark entity detected

        # print some info messages
        host.logMsg(
            "   Found GENERATION entity  : " + entity_generation + "\t - " +
            str(["%s:%s" % (str(attr["name"]), str(attr["value"])) for attr in
                 spb_eon.entities_eond[entity_generation].attributes.get_dictionary()])
        )

        pv = IeconPvDev(
            host=host,
            iecon_scada=spb_scada,
            eon_name=spb_eon_name,
            eond_name=entity_generation,
            influx=True
        )
        pv.timeBase = host.timeBase  # Timebase of the dataset, not the simulation!
        pv.strictComfort = not host.useIslanding
        sm.addDevice(pv)

        pvpc = IeconLivePvCtrl(
            name=entity_generation,
            dev=pv,
            ctrl=ctrl,
            sun=sun,
            host=host
        )
        pvpc.log_db_measurement = spb_eon_name  # Force DB log values to be written in the EoN DB Measurement.
        pvpc.useEventControl = host.useEC
        pvpc.perfectPredictions = host.usePP
        pvpc.strictComfort = not host.useIslanding
        pvpc.islanding = host.useIslanding

    else:
        host.logWarning("   WARNING - This house doesn't have a GENERATION entity")

    # If there were no entities detected, the house controller will be removed.
    if not entities_detected:
        res = host.removeEntity(ctrl.name)
        host.logWarning("   WARNING - House controller removed from the simulation - " + str(res))

