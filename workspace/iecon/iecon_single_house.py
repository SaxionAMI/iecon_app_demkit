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

    This example is configured to run for a single house using the iecon-SERENE datastreams.
    This example creates DEMKIT objects for consumption, generation and hems.

    The reference iecon-SERENE house is: eiot-16eda211b788

    Note: that at IECON, we are relaying data to the Demkit VPS from the iecon-SERENE datastreams.
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
from dev.meterDev import MeterDev  # Meter device that aggregates the load of all individual devices

# Environment
from environment.live.openWeatherEnv import OpenWeatherEnv
from environment.live.metnoSunEnv import MetnoSunEnv

# Host, required to control/coordinate the simulation itself
from hosts.liveHost import LiveHost

# Controllers
from ctrl.congestionPoint import CongestionPoint  # Import a congestion point
from ctrl.groupCtrl import GroupCtrl  # Group controller to control multiple devices, implements Profile Steering

# IECON components
from mqtt_spb_wrapper import MqttSpbEntityScada

from iecon.dev.tools.ieconDevTools import iecon_eon_find_eond_by_attr
from iecon.dev.ieconLoadDev import IeconLoadDev
from iecon.dev.ieconPvDev import IeconPvDev

from iecon.ctrl.ieconLoadCtrl import IeconLoadCtrl
from iecon.ctrl.ieconLivePvCtrl import IeconLivePvCtrl

from iecon.database.ieconInfluxDB import IeconInfluxDB, IeconInfluxDBReader

# Load Demkit Configuration
from conf.usrconf import demCfg

from tools_iecon import iecon_eon_provision_demkit_components

SPB_DOMAIN_ID = demCfg.get("IECON_SPB_DOMAIN_ID", "IECON")
IECON_DEBUG_EN = demCfg.get("IECON_DEBUG_EN", False)
IECON_DEBUG_EN = True

SPB_EON_HOUSE = "eiot-16eda211b788"   # Specific house for this single simulation.
# SPB_EON_HOUSE = "eiot-012faeed6b29"
# SPB_EON_HOUSE = "eiot-3ad2398b76e8"

# Missing configuration?
if not demCfg["db"]["influx"]["address"]:
    sys.stderr.write("\nERROR -  unknown or missing configuration. Please check config.yml.\n")
    sys.stderr.write("Application finished !\n")
    exit(1)

# Create the main Host environment ( IMPORTANT and required ;) )
sim = LiveHost(name=SPB_DOMAIN_ID + "-ems-host")

# ---------------------------------------------------------------------------------------------------------------------
#       Simulation Configurations
# ---------------------------------------------------------------------------------------------------------------------

# Time configurations
sim.timezonestr = 'Europe/Amsterdam'            # This is not a pytz object for Astral!
sim.timezone = timezone(sim.timezonestr)     # Simulation timezone
sim.startTime = int(sim.timezone.localize(datetime(2024, 9, 24, 0, 0, 0)).timestamp())
sim.timeBase = 10
sim.ctrlTimeBase = 900                  # Timebase for controllers
sim.tickInterval = 10
sim.timeOffset = -1 * int(sim.timezone.localize(datetime(2024, 9, 24)).timestamp())
sim.alignplan = int(sim.timezone.localize(datetime(2024, 9, 24)).timestamp())

# Location parameters - For Sun modeling and predictions
sim.latitude = 52.330271  # OLST COORDINATES, NL
sim.longitude = 6.111991

# Data logging
sim.logDevices = False              # Enable log of device data
sim.logControllers = True           # NOTE: Controllers do not log so much, keep this on True (default)!
sim.logFlow = False                 # Enable log of flow data
sim.extendedLogging = False         # Enable extended logging
sim.enableDebug = IECON_DEBUG_EN    # Enable debug information

# Models and trained data persistence
sim.enablePersistence = False       # Restore data on restart (for demo purposes)

# Clear the database or not. NOTE If disabled, ensure that the database exists!!!
sim.clearDB = False

# Enable control:
# NOTE: AT MOST ONE OF THESE MAY BE TRUE! They can all be False, however
sim.useCtrl = True      # Use smart control, defaults to Profile steering
sim.useAuction = False  # Use an auction instead, NOTE useMC must be False!
sim.usePlAuc = False    # Use a planned auction instead (Profile steering planning, auction realization),
# NOTE useMC must be False!

# Specific options for control
sim.useCongestionPoints = False     # Use congestion points
sim.useMultipleCommits = False      # Commit multiple profiles at once in profile steering
sim.useChildPruning = False         # Remoce children after each iteration that haven't provided substantial imporvement
sim.useIslanding = False            # Use islanding mode, only works with auction based control at the moment

sim.useEC = True  # Use Event-based control
sim.usePP = False  # Use perfect predictions (a.k.a no predictions)
sim.useQ = False  # Perform reactive ELECTRICITY optimization
sim.useMC = False  # Use three phases and multi-commodity control

# Check some necessary things
if sim.useMC:
    assert (sim.useAuction is False)
    assert (sim.usePlAuc is False)

# ---------------------------------------------------------------------------------------------------------------------
#       Simulation components instantiation
# ---------------------------------------------------------------------------------------------------------------------

# Initialize the random seed. Not required, but definitely preferred
random.seed(1337)

# Use the IECON InfluxDB2x - Historic data is retrieved from stored raw IECON spB data.
# A New EoN ems-demkit-<SPB_GROUP> is created, and all related demkit simulation data will be contained inside this spB EoN
sim.db = IeconInfluxDB(host=sim)

# Settings for Weather services
weather = OpenWeatherEnv("weather-openweather", sim)
weather.apiKey = demCfg.get("openweather_api_key", "")

# Settings for Sun services
sun = MetnoSunEnv("sun-forec-Metno", sim)
sun.api_user_agent = demCfg.get("metno_api_user_agent", "")  # Get the user agent from the configuration file

# FIX for IECON specific InfluxDBReader, only if DB is IeconInfluxDB class.
# SUN data is located under EoN=db.eon_name, EoND=Sun.name
if sim.db.__class__.__name__ == "IeconInfluxDB":
    sun.reader = IeconInfluxDBReader(host=sim,
                                     db_measurement=sim.db.database_measurement,
                                     entity_name=sun.name,
                                     field_name="GHI")


# --- IECON ---  Create the SCADA object to handle device discovery, realtime data updates and send commands
iecon_scada = MqttSpbEntityScada(
    spb_domain_name=SPB_DOMAIN_ID,
    spb_scada_name="ems-demkit",
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
sim.logMsg("  EoN: " + ", ".join(iecon_scada.entities_eon.keys()))

# scada.publish_birth()  # (Commented so the scada is not published in spb - ghost app) Send birth message for the SCADA application

# -------- SINGLE HOUSE IECON ----------------

sim.logMsg("---- IECON SCADA automatic edge / EoN (House) entity detection ----")

# Provision of Demkit component for IECON spB Edge / EoN / HOUSE entities ( Consumption, Generation, Supply )
iecon_eon_provision_demkit_components(
    host=sim,
    sun=sun,
    spb_scada=iecon_scada,
    spb_eon_name=SPB_EON_HOUSE,
)

sim.logMsg("----")

# The last thing to do is starting the simulation!
sim.startSimulation()

