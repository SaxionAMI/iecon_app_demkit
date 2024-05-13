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

from datetime import datetime
from pytz import timezone

import random




### MODULES ###
# Import the modules that you require for the model
# Devices
from dev.loadDev import LoadDev				# Static load device model
from dev.live.hassLoadDev import HassLoadDev 	# Read a sensor from Hass

# Environment
from environment.sunEnv import SunEnv
from environment.weatherEnv import WeatherEnv
from environment.live.openWeatherEnv import OpenWeatherEnv
from environment.live.solcastSunEnv import SolcastSunEnv

from dev.meterDev import MeterDev			# Meter device that aggregates the load of all individual devices

# Host, required to control/coordinate the simulation itself
from hosts.liveHost import LiveHost

# Controllers
from ctrl.congestionPoint import CongestionPoint	# Import a congestion point
from ctrl.loadCtrl import LoadCtrl			# Static load controller for predictions
from ctrl.live.livePvCtrl import LivePvCtrl
from ctrl.groupCtrl import GroupCtrl		# Group controller to control multiple devices, implements Profile Steering




# General settings - Locale
timeZone = timezone('Europe/Amsterdam')
startTime = int(timeZone.localize(datetime(2018, 1, 29)).timestamp())
timeOffset = -1 * int(timeZone.localize(datetime(2018, 1, 1)).timestamp())
alignplan = int(timeZone.localize(datetime(2019, 2, 13)).timestamp())

latitude = 	52.330271	# OLST COORDINATES
longitude = 6.111991
timeZoneStr = 'Europe/Amsterdam' # This is not a pytz object for Astral!


# Logging:
logDevices = True

# Restore data on restart (for demo purposes)
enablePersistence = True

database = "dem"
dataPrefix = ""











##### HERE STARTS THE REAL MODEL DEFINITION OF THE HOUSE TO BE SIMULATED #####
# First we need to instantiate the Host environment:
sim = LiveHost()

sim.timeBase = 10
sim.tickInterval = 10
sim.timeOffset = timeOffset
sim.timezone = timeZone
sim.timezonestr = timeZoneStr
sim.latitude = latitude
sim.longitude = longitude

sim.db.database = database
sim.db.prefix = dataPrefix
sim.logDevices = logDevices
sim.logControllers = True 	# NOTE: Controllers do not log so much, keep this on True (default)!
sim.logFlow = False
sim.enablePersistence = enablePersistence






# Not needed stuff for now, but kept as reference

# # Settings for Weather services
# weather = OpenWeatherEnv("Weather", sim)
# weather.apiKey = ""

# sun = SolcastSunEnv("Sun", sim)
# sun.apiKey = ""




# Definition of a house config
sm = MeterDev("METER",  sim) #params: name, simHost


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


# The last thing to do is starting the simulation!
sim.startSimulation()





## OTHER STUFF FOR REFERENCE

# ADDING A HEMS
#add a controller if necessary
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
