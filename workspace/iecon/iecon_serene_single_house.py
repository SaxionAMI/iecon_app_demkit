# Copyright 2023 University of Twente

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    --- IECON Example ---

    This example is configured to run for a single house using the SERENE datastreams.
    This example creates DEMKIT objects for consumption, generation and hems.

    The reference SERENE house is: eiot-16eda211b788

    Note: that at IECON, we are relaying data to the Demkit VPS from the SERENE datastreams.
    Creating an environment for testing, where the real data streams or database are not affected by the testing

    The demkit InfluxDB is modified for ieconInfluxDB class, to inject the demkit data generated on a
    spB edge node called emsDemkit-<DOMAIN>. The InfluxReader is also modified to get data directly from
    IECON InfluxDBn formated DB, which it is automatically stored from real time data by IECON application.

"""

import sys
import time
import random
from datetime import datetime
from pytz import timezone

### MODULES ###
# Import the modules that you require for the model
# Devices
from dev.loadDev import LoadDev  # Static load device model
from dev.live.hassLoadDev import HassLoadDev  # Read a sensor from Hass

# Environment
from environment.sunEnv import SunEnv
from environment.weatherEnv import WeatherEnv
from environment.live.openWeatherEnv import OpenWeatherEnv
from environment.live.solcastSunEnv import SolcastSunEnv

from dev.meterDev import MeterDev  # Meter device that aggregates the load of all individual devices

# Host, required to control/coordinate the simulation itself
from hosts.liveHost import LiveHost

# Controllers
from ctrl.congestionPoint import CongestionPoint  # Import a congestion point
from ctrl.loadCtrl import LoadCtrl  # Static load controller for predictions
from ctrl.live.livePvCtrl import LivePvCtrl
from ctrl.groupCtrl import GroupCtrl  # Group controller to control multiple devices, implements Profile Steering

# IECON components
from mqtt_spb_wrapper import MqttSpbEntityScada
from iecon.dev.tools.ieconDevTools import iecon_eon_find_eond_by_attr
from iecon.dev.ieconLoadDev import IeconLoadDev
from iecon.dev.ieconPvDev import IeconPvDev
from iecon.database.ieconInfluxDB import IeconInfluxDB, IeconInfluxDBReader

# Load Demkit Configuration
from conf.usrconf import demCfg

SPB_DOMAIN_ID = demCfg.get("IECON_SPB_DOMAIN_ID", "IECON")
IECON_DEBUG_EN = demCfg.get("IECON_DEBUG_EN", False)
IECON_DEBUG_EN = True

SPB_EON_HOUSE = "eiot-16eda211b788"   # Specific house for this single simulation.

# Missing configuration?
if not demCfg["db"]["influx"]["address"]:
    sys.stderr.write("\nERROR -  unknown or missing configuration. Please check config.yml.\n")
    sys.stderr.write("Application finished !\n")
    exit(1)

# ---------------------------------------------------------------------------------------------------------------------
# --- General settings - Locale --------------------------------------------------------------------------------------

timeZone = timezone('Europe/Amsterdam')
startTime = int(timeZone.localize(datetime(2024, 9, 24, 0, 0, 0)).timestamp())
timeOffset = -1 * int(timeZone.localize(datetime(2024, 9, 24)).timestamp())
alignplan = int(timeZone.localize(datetime(2025, 9, 24)).timestamp())

latitude = 52.330271  # OLST COORDINATES
longitude = 6.111991
timeZoneStr = 'Europe/Amsterdam'  # This is not a pytz object for Astral!

# Logging:
logDevices = True

# Restore data on restart (for demo purposes)
enablePersistence = False

# Enable control:
# NOTE: AT MOST ONE OF THESE MAY BE TRUE! They can all be False, however
useCtrl = True  # Use smart control, defaults to Profile steering
useAuction = False  # Use an auction instead, NOTE useMC must be False!
usePlAuc = False  # Use a planned auction instead (Profile steering planning, auction realization),
# NOTE useMC must be False!

# Specific options for control
useCongestionPoints = False  # Use congestion points
useMultipleCommits = False  # Commit multiple profiles at once in profile steering
useChildPruning = False  # Remoce children after each iteration that haven't provided substantial imporvement
useIslanding = False  # Use islanding mode, only works with auction based control at the moment

ctrlTimeBase = 900  # Timebase for controllers
useEC = True  # Use Event-based control
usePP = False  # Use perfect predictions (a.k.a no predictions)
useQ = False  # Perform reactive ELECTRICITY optimization
useMC = False  # Use three phases and multi-commodity control
clearDB = False  # Clear the database or not. NOTE If disabled, ensure that the database exists!!!
# Note either EC or PP should be enabled

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

if useMC:
    assert (useAuction is False)
    assert (usePlAuc is False)

# MODEL CREATION
# Now it is time to create the complete model using the loaded modules
if useMC:
    commodities = ['EL1', 'EL2', 'EL3']
    weights = {'EL1': (1 / 3), 'EL2': (1 / 3), 'EL3': (1 / 3)}

# Initialize the random seed. Not required, but definitely preferred
random.seed(1337)

# ---- HERE STARTS THE REAL MODEL DEFINITION OF THE HOUSE TO BE SIMULATED ----
# First we need to instantiate the Host environment:
sim = LiveHost(name="host-"+SPB_DOMAIN_ID)

# Use the IECON InfluxDB2x - Historic data is retrieved from stored raw IECON spB data.
# A New EoN emsDemkit-<DOMAIN> is created, and all related demkit simulation data will be contained inside this spB EoN
sim.db = IeconInfluxDB(host=sim)

sim.startTime = startTime
sim.timeBase = 10
sim.tickInterval = 10
sim.timeOffset = timeOffset
sim.timezone = timeZone
sim.timezonestr = timeZoneStr
sim.latitude = latitude
sim.longitude = longitude

sim.logDevices = logDevices
sim.logControllers = True  # NOTE: Controllers do not log so much, keep this on True (default)!
sim.logFlow = False
sim.enablePersistence = enablePersistence
sim.extendedLogging = False
sim.enableDebug = IECON_DEBUG_EN

# Not needed stuff for now, but kept as reference

# Settings for Weather services
weather = OpenWeatherEnv("Weather", sim)
weather.apiKey = demCfg.get("openweather_api_key", "")


# Settings for Sun services
sun = SolcastSunEnv("sun-"+sim.db.database, sim)
sun.apiKey = demCfg.get("solcast_api_key", "")  # Get the key from the configuration file

# FIX for IECON specific InfluxDBReader, only if DB is IeconInfluxDB class.
# SUN data is located under EoN=db.eon_name, EoND=Sun.name
if sim.db.__class__.__name__ == "IeconInfluxDB":
    sun.reader = IeconInfluxDBReader(host=sim, eon_name=sim.db.eon_name, eond_name=sun.name, field_name="GHI")


# --- IECON ---  Create the SCADA object to handle device discovery, data updates and send commands
iecon_scada = MqttSpbEntityScada(
    spb_domain_name=SPB_DOMAIN_ID,
    spb_scada_name="demkit-ems",
    debug_enabled=False,  # IECON_DEBUG_EN,
)

# Connect to the MQTT spB broker
_connected = False
while not _connected:
    sim.logMsg(
        "Connecting to IECON data broker %s:%d ..." % (demCfg["IECON_MQTT_HOST"], demCfg["IECON_MQTT_PORT"])
    )

    _connected = iecon_scada.connect(
        host=demCfg["IECON_MQTT_HOST"],
        port=demCfg["IECON_MQTT_PORT"],
        user=demCfg["IECON_MQTT_USER"],
        password=demCfg["IECON_MQTT_PASS"],
    )

    if not _connected:
        sim.logWarning("  Error, could not connect. Trying again in a few seconds ...")
        time.sleep(3)

sim.logMsg("Connected to IECON data broker, waiting SCADA to be initialized. . .")

while not iecon_scada.is_initialized():
    time.sleep(0.1)

sim.logMsg("IECON SCADA object initialized, detected %d edge entities in the domain." % len(iecon_scada.entities_eon))

# scada.publish_birth()  # (Commented so the scada is not published in spb - ghost app) Send birth message for the SCADA application

# -------- SINGLE HOUSE IECON ----------------

sim.logMsg("---- IECON SCADA automatic neighbourhood entity detection ----")

eon_name = SPB_EON_HOUSE    # EoN ID name
eon = iecon_scada.entities_eon[eon_name]  # Get the EoN object, to search over the devices

sim.logMsg("- Searching EoN <%s> for devices CONSUMPTION, GENERATION, ... " % eon_name)

# Search for CONSUMPTION
entity_consumption = iecon_eon_find_eond_by_attr(
    eon=eon,
    eond_attributes={
        'CTYPEC': "consumption",
        "CTYPE": "electricity",
        "ETYPE": "powermeter",
    },
)

# Search for GENERATION
entity_generation = iecon_eon_find_eond_by_attr(
    eon=eon,
    eond_attributes={
        'CTYPEC': "generation",
        "CTYPE": "electricity",
    },
)


# ---- DEMKIT Registration of entities ------------------------------------

# ADDING A HEMS - add a controller if necessary
if useCongestionPoints:
    cp = CongestionPoint()
    cp.setUpperLimit('ELECTRICITY', 3 * 25 * 230)  # 3 phase 25A connection ELECTRICITY limits
    cp.setLowerLimit('ELECTRICITY', -3 * 25 * 230)

if useCongestionPoints:
    ctrl = GroupCtrl("hems-" + eon_name, sim, None, cp)
else:
    ctrl = GroupCtrl("hems-" + eon_name, sim, None)  # params: name, simHost
    ctrl.minImprovement = 0.01
    if useMultipleCommits:
        ctrl.maxIters = 4
    else:
        ctrl.maxIters = 8
    ctrl.timeBase = ctrlTimeBase  # 900 is advised hre, must be a multiple of the simulation timeBase
    ctrl.useEventControl = useEC  # Enable / disable event-based control
    ctrl.isFleetController = True  # Very important to set this right in case of large structures. The root controller
    # needs to be a fleetcontroller anyways. See 4.3 of Hoogsteen's thesis
    ctrl.strictComfort = not useIslanding
    ctrl.islanding = useIslanding
    ctrl.planHorizon = 2 * int(24 * 3600 / ctrlTimeBase)
    ctrl.planInterval = int(24 * 3600 / ctrlTimeBase)
    ctrl.predefinedNextPlan = alignplan


# --- HOUSE METER ( supply point at DEMKIT )
sm = MeterDev(name="housesm-" + eon_name, host=sim)
sm.infuxTagsExtraLog["eon"] = eon_name  # Set the EoN value


# --- CONSUMPTION ---- Add house consumption to the house
if entity_consumption:

    # Print some information
    sim.logMsg("  Found CONSUMPTION entity : " + entity_consumption)
    for attr in eon.entities_eond[entity_consumption].attributes.get_dictionary():
        sim.logMsg("      %s : %s" % (str(attr["name"]), str(attr["value"])))

    load = IeconLoadDev(
        host=sim,
        iecon_scada=iecon_scada,
        eon_name=eon_name,
        eond_name=entity_consumption,
        influx=True,
    )
    load.timeBase = sim.timeBase  # Timebase of the dataset, not the simulation!
    load.strictComfort = not useIslanding
    sm.addDevice(load)

    loadctrl = LoadCtrl(
        name="loadctrl-" + load.name,
        dev=load,
        ctrl=ctrl,
        host=sim
    )
    loadctrl.perfectPredictions = usePP  # Use perfect predictions or not
    loadctrl.useEventControl = useEC  # Use event-based control
    loadctrl.timeBase = ctrlTimeBase  # TimeBase for controllers
    loadctrl.strictComfort = not useIslanding
    loadctrl.islanding = useIslanding

else:
    sim.logWarning("  This house doesn't have a CONSUMPTION entity, house is skipped from demkit!")


# --- PV ---- Solar panel based on provided data -----------------------------------------------
if entity_generation:

    # print some info messages
    sim.logMsg("  Found GENERATION entity : " + entity_generation)
    for attr in eon.entities_eond[entity_generation].attributes.get_dictionary():
        sim.logMsg("      %s : %s" % (str(attr["name"]), str(attr["value"])))

    pv = IeconPvDev(
        host=sim,
        iecon_scada=iecon_scada,
        eon_name=eon_name,
        eond_name=entity_generation,
        influx=True
    )
    pv.timeBase = sim.timeBase  # Timebase of the dataset, not the simulation!
    pv.strictComfort = not useIslanding
    sm.addDevice(pv)

    pvpc = LivePvCtrl("pvctrl-" + pv.eond_name, pv, ctrl, sun, sim)
    pvpc.useEventControl = useEC
    pvpc.perfectPredictions = usePP
    pvpc.strictComfort = not useIslanding
    pvpc.islanding = useIslanding

else:
    sim.logWarning("  This house doesn't have a GENERATION entity, house is skipped from demkit!")


# The last thing to do is starting the simulation!
sim.startSimulation()



















## OTHER STUFF FOR REFERENCE

# ADDING A HEMS
# add a controller if necessary
# if useCongestionPoints:
# cp = CongestionPoint()
# cp.setUpperLimit('ELECTRICITY', 3*25*230) # 3 phase 25A connection ELECTRICITY limits
# cp.setLowerLimit('ELECTRICITY', -3*25*230)

# if useCongestionPoints:
# ctrl = GroupCtrl("OlstCtrl",  sim , None, cp)
# else:
# ctrl = GroupCtrl("OlstCtrl",  sim , None) #params: name, simHost
# ctrl.minImprovement = 0.01
# if useMultipleCommits:
# ctrl.maxIters = 4
# else:
# ctrl.maxIters = 8
# ctrl.timeBase = ctrlTimeBase	# 900 is advised hre, must be a multiple of the simulation timeBase
# ctrl.useEventControl = useEC	# Enable / disable event-based control
# ctrl.isFleetController = True 	# Very important to set this right in case of large structures. The root controller needs to be a fleetcontroller anyways. See 4.3 of Hoogsteen's thesis
# ctrl.strictComfort = not useIslanding
# ctrl.islanding = useIslanding
# ctrl.planHorizon = 2*int(24*3600/ctrlTimeBase)
# ctrl.planInterval = int(24*3600/ctrlTimeBase)
# ctrl.predefinedNextPlan = alignplan


# unc = HassLoadDev("LOAD",  sim, influx=True) #params: name, simHost
# unc.url = ""
# unc.bearer = ""
# unc.sensor = "sensor.total_power" # Sensor name as known to Home Assistant
# unc.timeBase = timeBase		# Timebase, NOTE this is the timebase of the dataset and not the simulation!
# unc.strictComfort = not useIslanding
# unc.infuxTags = {"name": "LOAD"} # Needed to get the load from the database
# sm.addDevice(unc)

# uncc = LoadCtrl("LOADCTRL", unc, ctrl, sim) 	# params: name, device, higher-level controller, simHost
# uncc.perfectPredictions = usePP							# Use perfect predictions or not
# uncc.useEventControl = useEC							# Use event-based control
# uncc.timeBase = ctrlTimeBase							# TimeBase for controllers
# if useMC:
# uncc.commodities = []								# Clear the list
# uncc.commodities.append(commodities[phase-1])		# Add applicable commodity
# uncc.weights = dict(weights)						# Overwrite the weights
# uncc.strictComfort = not useIslanding
# uncc.islanding = useIslanding


# # Solar panel based on provided data
# pv = PvOutputDev("PV", sim, influx=True, sun=sun)  # params: name, device, higher-level controller, simHost
# pv.url = 'https://pvoutput.org/intraday.jsp?id=87532&sid=77615'
# pv.scaling = 1
# pv.timeBase = timeBase  # Timebase of the dataset, not the simulation!
# pv.strictComfort = not useIslanding
# pv.infuxTags = {"name": "PV"} # Needed to get the load from the database

# # Note, in all these settings you will need to provide an index (first element).
# # Based on the houseNum, this index can be obtained using the alpg.indexFromFile helper!
# # e.g:
# # idx = alpg.indexFromFile("dataPhotovoltaicSettings.txt", houseNum)
# # and then use e.g.:

# sm.addDevice(pv)

# pvpc = LivePvCtrl("PVCTRL", pv, ctrl, sun, sim)
# pvpc.useEventControl = useEC
# pvpc.perfectPredictions = usePP
# pvpc.strictComfort = not useIslanding
# pvpc.islanding = useIslanding


# # BATTERY
# #add a battery
# # Follows very much the same reasoning as with the EV above, so the documentation is sparse here
# buf = BufDev("BAT", sim, sm, ctrl)		# params: name, simHost
# #Set the parameters
# buf.chargingELECTRICITYs = [-10000,10000]
# buf.discrete = False

# buf.capacity = 40000
# buf.initialSoC = initialSoC
# buf.soc = initialSoC

# # Marks to spawn events
# buf.highMark = buf.capacity*0.9
# buf.lowMark = buf.capacity*0.1

# buf.strictComfort = not useIslanding
# sm.addDevice(buf)


# bufc = BufCtrl("BATCTRL",  buf,  ctrl,  sim) 	# params: name, device, higher-level controller, simHost
# bufc.useEventControl = useEC
# bufc.timeBase = ctrlTimeBase
# if useMC:
# bufc.weights = dict(weights)
# bufc.commodities = []
# bufc.commodities.append(commodities[phase-1])
# bufc.strictComfort = not useIslanding
# bufc.islanding = useIslanding
# bufc.replanInterval = [900,900]

# # No control, add the battery to the smart meter
# buf.meter = sm
# buf.balancing = True


# ########## Adding the first house
# sm = MeterDev("H1-METER",  sim) #params: name, simHost

# # Load model of this house
# load = SedconLoadDev("H1-LOAD", sim, influx=True)  # params: name, device, higher-level controller, simHost
# load.url = "http://sedconbroker_nossl:5000"
# load.username = "demkit"
# load.password = "hGsgbY2020!"
# load.meterid = 1
# load.timeBase = timeBase  # Timebase of the dataset, not the simulation!
# load.strictComfort = not useIslanding
# load.infuxTags = {"name": "H1-LOAD"} # Needed to get the load from the database

# sm.addDevice(load)

# # Load controller
# loadc = LoadCtrl("H1-LOADCTRL", load, ctrl, sim) 	# params: name, device, higher-level controller, simHost
# load.perfectPredictions = usePP							# Use perfect predictions or not
# loadc.useEventControl = useEC							# Use event-based control
# loadc.timeBase = ctrlTimeBase							# TimeBase for controllers
# loadc.strictComfort = not useIslanding
# loadc.islanding = useIslanding


# # Solar panel based on provided data
# pv = SedconPvDev("H1-PV", sim, influx=True, sun=sun)  # params: name, device, higher-level controller, simHost
# pv.url = "http://sedconbroker_nossl:5000"
# pv.username = "demkit"
# pv.password = "hGsgbY2020!"
# pv.meterid = 1
# pv.timeBase = timeBase  # Timebase of the dataset, not the simulation!
# pv.strictComfort = not useIslanding
# pv.infuxTags = {"name": "H1-PV"} # Needed to get the load from the database

# # Note, in all these settings you will need to provide an index (first element).
# # Based on the houseNum, this index can be obtained using the alpg.indexFromFile helper!
# # e.g:
# # idx = alpg.indexFromFile("dataPhotovoltaicSettings.txt", houseNum)
# # and then use e.g.:

# sm.addDevice(pv)

# pvpc = LivePvCtrl("H1-PVCTRL", pv, ctrl, sun, sim)
# pvpc.useEventControl = useEC
# pvpc.perfectPredictions = usePP
# pvpc.strictComfort = not useIslanding
# pvpc.islanding = useIslanding
