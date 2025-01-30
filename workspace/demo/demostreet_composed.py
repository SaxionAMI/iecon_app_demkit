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

import random

### MODULES ###
# Import the modules that you require for the model
# Devices
from dev.loadDev import LoadDev				# Static load device model
from dev.curtDev import CurtDev				# Also a static load, but one that van be turned off (curtailed/shed)
from dev.btsDev import BtsDev				# BufferTimeShiftable Device, used for electric vehicles
from dev.tsDev import TsDev					# Timeshiftable Device, used for whitegoods
from dev.bufDev import BufDev				# Buffer device, used for storage, such as batteries
from dev.bufConvDev import BufConvDev		# BufferConverter device, used for heatpumps with heat store

from dev.electricity.solarPanelDev import SolarPanelDev			# Solar panel
from dev.thermal.solarCollectorDev import SolarCollectorDev 	# solar collector

# Thermal Devices
from dev.thermal.zoneDev2R2C import ZoneDev2R2C
from dev.thermal.zoneDev1R1C import ZoneDev1R1C
from dev.thermal.heatSourceDev import HeatSourceDev
from dev.thermal.thermalBufConvDev import ThermalBufConvDev
from dev.thermal.heatPumpDev import HeatPumpDev
from dev.thermal.combinedHeatPowerDev import CombinedHeatPowerDev
from dev.thermal.gasBoilerDev import GasBoilerDev
from dev.thermal.dhwDev import DhwDev
from ctrl.thermal.thermostat import Thermostat

# Environment
from environment.sunEnv import SunEnv
from environment.weatherEnv import WeatherEnv

from dev.meterDev import MeterDev			# Meter device that aggregates the load of all individual devices

# Host, required to control/coordinate the simulation itself
from hosts.simHost import SimHost			# Platform Host, in this case a simulation basis to perform simulations


# Controllers
from ctrl.congestionPoint import CongestionPoint	# Import a congestion point
from ctrl.loadCtrl import LoadCtrl			# Static load controller for predictions
from ctrl.curtCtrl import CurtCtrl			# Static Curtailable load controller for predictions
from ctrl.btsCtrl import BtsCtrl    		# BufferTimeShiftable Controller
from ctrl.tsCtrl import TsCtrl				# Timeshiftable controller
from ctrl.bufCtrl import BufCtrl			# Buffer controller
from ctrl.bufConvCtrl import BufConvCtrl 	# BufferConverter

from ctrl.groupCtrl import GroupCtrl		# Group controller to control multiple devices, implements Profile Steering
from ctrl.admm.admmGroupCtrl import AdmmGroupCtrl

from ctrl.thermal.thermalBufConvCtrl import ThermalBufConvCtrl

from ctrl.auction.btsAuctionCtrl import BtsAuctionCtrl
from ctrl.auction.tsAuctionCtrl import TsAuctionCtrl
from ctrl.auction.bufAuctionCtrl import BufAuctionCtrl
from ctrl.auction.bufConvAuctionCtrl import BufConvAuctionCtrl
from ctrl.auction.loadAuctionCtrl import LoadAuctionCtrl
from ctrl.auction.curtAuctionCtrl import CurtAuctionCtrl
from ctrl.auction.aggregatorCtrl import AggregatorCtrl
from ctrl.auction.auctioneerCtrl import AuctioneerCtrl
from ctrl.auction.thermal.thermalBufConvAuctionCtrl import ThermalBufConvAuctionCtrl

# Planned Auction controllers, follows same reasoning
from ctrl.plannedAuction.paBtsCtrl import PaBtsCtrl
from ctrl.plannedAuction.paLoadCtrl import PaLoadCtrl
from ctrl.plannedAuction.paCurtCtrl import PaCurtCtrl
from ctrl.plannedAuction.paBufCtrl import PaBufCtrl
from ctrl.plannedAuction.paBufConvCtrl import PaBufConvCtrl
from ctrl.plannedAuction.paTsCtrl import PaTsCtrl
from ctrl.plannedAuction.paGroupCtrl import PaGroupCtrl	
from ctrl.plannedAuction.thermal.thermalPaBufConvCtrl import ThermalPaBufConvCtrl

# Import physical network
from flow.el.lvNode import LvNode
from flow.el.lvCable import LvCable
from flow.el.elLoadFlow import ElLoadFlow

# Readers
from util.csvReader import CsvReader
from util.funcReader import FuncReader

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

timeZone = timezone('Europe/Amsterdam')
startTime = int(timeZone.localize(datetime(2023, 1, 29)).timestamp())
timeOffset = -1 * int(timeZone.localize(datetime(2023, 1, 1)).timestamp())

timeBase = 60 # Default timebase
intervals = 7*24*int(3600/timeBase)	# Simulating 7 days of data (calculations based on the timeBase)

# Number of houses, not used in the demohouse:
numOfHouses = 10

# Data storage settings
database = 'dem'					# Database to store results
dataPrefix = ''						# A prefix (optional) can be used to put multiple simulations in one database conveniently. NOTE: Disable the cleardatabase!
clearDB = True						# Clear the database or not. !


# ALPG input
alpgFolder = 'alpg/output/demo/'
useALPG = True	# Use ALPG data

# Logging:
logDevices = True				# When disabled, only overall stats will be logged which saves simulation time to quickly estimate the effects of settings
extendedLogging = False			# Extended logging adds more information (such as reactive power) but slows down the simulation

# Restore data on restart (for demo purposes)
enablePersistence = False

# Enable control:
# NOTE: AT MOST ONE OF THESE MAY BE TRUE! They can all be False, however
useCtrl = True		# Use smart control, defaults to Profile steering
useAuction = False	# Use an auction instead, NOTE useMC must be False!
usePlAuc = False	# Use a planned auction instead (Profile steering planning, auction realization), NOTE useMC must be False!
useAdmm = False		# USe ADMM optimization (under development), only limited options available (usePP, useEC)

# Specific options for control
useCongestionPoints = False	# Use congestionpoints
useIslanding = False		# Use islanding mode

# Specific for device control:
useFillMethod = True		# Use a sort of valley filling approach with only the battery

ctrlTimeBase = 900		# Timebase for controllers
useEC = True			# Use Event-based control
usePP = False			# Use perfect predictions (a.k.a no predictions)
useQ = False			# Perform reactive power optimization
useMC = False			# Use three phases and multicommodity control
# Note either EC or PP should be enabled

pricesElectricity = None #Insert a file, e.g. 'data/prices/apx.csv'
# pricesElectricity = CsvReader(dataSource='data/prices/apx.csv', timeBase=timeBase, column=0, timeOffset=timeOffset)
profileWeight = 1 # For only steering on prices, set to 0. Floats allowed as weight between prices / profile steering

# Example with putting a sine as a price signal instead:
# pricesElectricity = FuncReader(timeOffset = timeOffset)
# pricesElectricity.functionType = "sin"
# pricesElectricity.period = 12*3600
# pricesElectricity.amplitude = -5000
# pricesElectricity.dutyCycle = 0.5
# pricesElectricity.powerOffset = 2500
# profileWeight = 0



# NOTE: No need to modify lines below
if useMC:
	assert(useAuction == False)
	assert(usePlAuc == False)
	assert(useAdmm == False)

### MODEL CREATION ####

# Now it is time to create the complete model using the loaded modules
if useMC:
	commodities = ['EL1', 'EL2', 'EL3']
	weights = {'EL1': (1/3), 'EL2': (1/3), 'EL3': (1/3)}
else:
	commodities = ['ELECTRICITY']
	weights = {'ELECTRICITY': 1}

# Initialize the random seed. Not required, but definitely preferred
random.seed(1337)
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

# Utils
import util.alpg as alpg
# This example shows how to configure a simple model of one household.
# It can be used to test if everything is working correctly
# but also as a template for new models

# Usually we create a couple of global variables which we use for some general settings
# The idea is that we can easily change these parameters for different cases
# Think of using/not using control, or the amount of data to be logged
# Some general, and often useful, variables are:

# Read in raw ALPG output data to configure devices
try:
	ev_starttimes = alpg.listFromFile(alpgFolder+'ElectricVehicle_Starttimes.txt')
	ev_endtimes = alpg.listFromFile(alpgFolder+'ElectricVehicle_Endtimes.txt')
	ev_energy = alpg.listFromFile(alpgFolder+'ElectricVehicle_RequiredCharge.txt')
	ev_specs = alpg.listFromFile(alpgFolder+'ElectricVehicle_Specs.txt')

	wm_starttimes = alpg.listFromFile(alpgFolder+'WashingMachine_Starttimes.txt')
	wm_endtimes = alpg.listFromFile(alpgFolder+'WashingMachine_Endtimes.txt')

	dw_starttimes = alpg.listFromFile(alpgFolder+'Dishwasher_Starttimes.txt')
	dw_endtimes = alpg.listFromFile(alpgFolder+'Dishwasher_Endtimes.txt')

	pv_specs = alpg.listFromFile(alpgFolder+'PhotovoltaicSettings.txt')
	bat_specs = alpg.listFromFile(alpgFolder+'BatterySettings.txt')

	therm_starttimes = alpg.listFromFile(alpgFolder+'Thermostat_Starttimes.txt')
	therm_setpoints = alpg.listFromFile(alpgFolder+'Thermostat_Setpoints.txt')

	heat_specs = alpg.listFromFileStr(alpgFolder+'HeatingSettings.txt')
except:
	print("[ERROR] An error occurred when reading ALPG input data. \n\tPossible causes: \n\t  -Have you generated the data (refer to the README)? \n\t  -Is the variable alpgFolder configured correctly?")
	exit()
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

##### HERE STARTS THE REAL MODEL DEFINITION OF THE HOUSE TO BE SIMULATED #####
# First we need to instantiate the Host environment:
sim = SimHost()

#Some simulation settings
sim.timeBase = timeBase
sim.timeOffset = timeOffset
sim.timezone = timeZone
sim.intervals = intervals
sim.startTime = startTime
sim.db.database = database
sim.db.prefix = dataPrefix
# Use the following flags to log more/less details (significantly influences simulation speed)
sim.extendedLogging = extendedLogging
sim.logDevices = logDevices
sim.logControllers = True 	# NOTE: Controllers do not log so much, keep this on True (default)!
sim.logFlow = False
sim.enablePersistence = enablePersistence
if clearDB:
	sim.clearDatabase() 	# Removes and creates a database

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

# Initialize environmental devices
weather = WeatherEnv("Weather", sim)
weather.weatherFile = "data/weather/temperature.csv"

sun = SunEnv("Sun", sim)
sun.irradianceFile = 'data/weather/solarirradiation.csv'

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

# Now comes the house model
# This is defined as a function, such that multiple houses can be created easily
# Note that the following function is used in network models, so keeping it this way makes integration of networks convenient
def addHouse(node, coordx, coordy, phase, houseNum):
	# First add add a smart meter
	sm = MeterDev("SmartMeter-House-"+str(houseNum),  sim, list(commodities)) #params: name, simHost
	gm = MeterDev("SmartGasMeter-House-"+str(houseNum),  sim, commodities=['NATGAS'])

	if node is not None:
		node.addMeter(sm, phase)

# ADDING A HEMS
	#add a controller if necessary
	if useCongestionPoints:
		cph = CongestionPoint()
		if useMC:
			for c in commodities:
				cph.setUpperLimit(c, 15*230)
				cph.setLowerLimit(c, -15*230)
		else:
			cph.setUpperLimit('ELECTRICITY', 250) # 3 phase 25A connection power limits
			cph.setLowerLimit('ELECTRICITY', -250)


	if useCtrl:
		if useCongestionPoints:
			ctrl = GroupCtrl("HouseController-House-"+str(houseNum),  sim , rootctrl, cph)
		else:
			ctrl = GroupCtrl("HouseController-House-"+str(houseNum),  sim , rootctrl) #params: name, simHost
		ctrl.minImprovement = 0.001
		ctrl.timeBase = ctrlTimeBase	# 900 is advised hre, must be a multiple of the simulation timeBase
		ctrl.useEventControl = useEC	# Enable / disable event-based control
		ctrl.isFleetController = False 	# Very important to set this right in case of large structures. The root controller needs to be a fleetcontroller anyways. See 4.3 of Hoogsteen's thesis
		ctrl.initialPlan = True
		ctrl.simultaneousCommits = 1
		ctrl.strictComfort = not useIslanding

		ctrl.planHorizon = 2*int(24*3600/ctrlTimeBase)
		ctrl.planInterval = int(24*3600/ctrlTimeBase)
		ctrl.commodities = list(commodities)	# Overwrite the list of commodities
		ctrl.weights = dict(weights)			# Overwrite the weights


	# Or an auction (PowerMatcher) controller
	elif useAuction:
		# The real HEMS
		if useCongestionPoints:
			ctrl = AggregatorCtrl("HouseController-House-"+str(houseNum), rootctrl, sim, cph)
		else:
			ctrl = AggregatorCtrl("HouseController-House-"+str(houseNum), rootctrl, sim)

		ctrl.strictComfort = not useIslanding
		ctrl.islanding = useIslanding


	# Or a combination of the two
	elif usePlAuc:
		if useCongestionPoints:
			ctrl = PaGroupCtrl("HouseController-House-"+str(houseNum),  sim, rootctrl, cph)
		else:
			ctrl = PaGroupCtrl("HouseController-House-"+str(houseNum),  sim, rootctrl)
		ctrl.minImprovement = 0.0001
		ctrl.timeBase = ctrlTimeBase	# 900 is advised hre, must be a multiple of the simulation timeBase
		ctrl.useEventControl = useEC	# Enable / disable event-based control
		ctrl.isFleetController = False 	# Very important to set this right in case of large structures. The root controller needs to be a fleetcontroller anyways. See 4.3 of Hoogsteen's thesis
		ctrl.initialPlan = True 		# Recommended to speed up the process
		ctrl.commodities = list(commodities)	# Overwrite the list of commodities
		ctrl.weights = dict(weights)			# Overwrite the weights
		ctrl.strictComfort = not useIslanding
		ctrl.islanding = useIslanding
		ctrl.planHorizon = 2*int(24*3600/ctrlTimeBase)
		ctrl.planInterval = int(24*3600/ctrlTimeBase)

	elif useAdmm:
		# For now we only support one higher level controller, hence we use a simple object reference:
		ctrl = rootctrl
		# if useCongestionPoints:
		# 	ctrl = AdmmGroupCtrl("HouseController-House-"+str(houseNum),  sim , rootctrl, cp)
		# else:
		# 	ctrl = AdmmGroupCtrl("HouseController-House-"+str(houseNum),  sim , rootctrl) #params: name, simHost
		# ctrl.multipleCommits = False	# Allow multiple commits to speedup the optimization
		# ctrl.maxIters = 20
		# ctrl.timeBase = ctrlTimeBase	# 900 is advised hre, must be a multiple of the simulation timeBase
		# ctrl.useEventControl = useEC	# Enable / disable event-based control
		# ctrl.isFleetController = True 	# Very important to set this right in case of large structures. The root controller needs to be a fleetcontroller anyways. See 4.3 of Hoogsteen's thesis
		# ctrl.initialPlan = False 		# Recommended to speed up the process
		# ctrl.strictComfort = True
		# ctrl.islanding = False
		# ctrl.planHorizon = 2*int(24*3600/ctrlTimeBase)
		# ctrl.planInterval = int(24*3600/ctrlTimeBase)
		#
		# ctrl.commodities = list(commodities)	# Overwrite the list of commodities
		# ctrl.weights = dict(weights)			# Overwrite the weights

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

# STATIC LOAD
	#add a lumped uncontrollable load
	unc = CurtDev("Load-House-"+str(houseNum),  sim) #params: name, simHost
	unc.filename = alpgFolder+'Electricity_Profile.csv' 						# Specify the file for active power
	unc.filenameReactive = alpgFolder+'Reactive_Electricity_Profile.csv'		# Optional, specify the file for reactive power
	unc.column = houseNum
	unc.timeBase = 60		# Timebase, NOTE this is the timebase of the dataset and not the simulation!
	unc.strictComfort = not useIslanding

	if useMC:
		# Typically, one has to do the following with multiple commodities:
		unc.commodities = [(commodities[phase-1])]			# Add applicable commoditie(s)

	sm.addDevice(unc)

	# Optionally, add a controller to the device:
	if useCtrl or useAdmm:
		uncc = CurtCtrl("LoadController-House-"+str(houseNum), unc, ctrl, sim) 	# params: name, device, higher-level controller, simHost
		uncc.perfectPredictions = usePP							# Use perfect predictions or not
		uncc.useEventControl = useEC							# Use event-based control
		uncc.timeBase = ctrlTimeBase							# TimeBase for controllers

		uncc.commodities = list(unc.commodities)    		# Add applicable commodity
		uncc.weights = dict(weights)						# Overwrite the weights

	elif useAuction:
		uncc = CurtAuctionCtrl("LoadController-House-"+str(houseNum), unc, ctrl, sim)
		uncc.strictComfort = not useIslanding
		uncc.islanding = useIslanding

	elif usePlAuc:
		uncc = PaCurtCtrl("LoadController-House-"+str(houseNum), unc, ctrl, sim)
		uncc.perfectPredictions = usePP							# Use perfect predictions or not
		uncc.useEventControl = useEC							# Use event-based control
		uncc.timeBase = ctrlTimeBase							# TimeBase for controllers
		uncc.strictComfort = not useIslanding
		uncc.islanding = useIslanding
	#From here on, same reasoning applies, so comments become sparse
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

# SOLAR PANEL SETUP
	# Add a solar pane
	idx = alpg.indexFromFile(alpgFolder+"PhotovoltaicSettings.txt", houseNum)

	if not useALPG or idx != -1:
		pv = SolarPanelDev("PV-House-" + str(houseNum), sim, sun) # <- see, here the sun object has to be provided ;)

		#Set the parameters
		if not useALPG:
			pv.size = 10*1.6		# in m2, (12 panels of 1.6 m2)
			pv.efficiency = 20		# efficiency in percent
			pv.azimuth = 180		# in degrees, 0=north, 90 is east, 180 is south
			pv.inclination = 35		# angle
		else:
			# Not using ALPG data
			pv.size = pv_specs[idx][3]			# in m2, (12 panels of 1.6 m2)
			pv.efficiency = pv_specs[idx][2]	# efficiency in percent
			pv.azimuth = pv_specs[idx][1]		# in degrees, 0=north, 90 is east
			pv.inclination = pv_specs[idx][0]	# angle

		pv.strictComfort = not useIslanding

		pv.commodities = commodities
		if useMC:
			pv.commodities = [commodities[phase - 1]]
			# Note, for a three phase inverter one needs to instantiate three separate PV instances!

		sm.addDevice(pv)

		# Add controllers
		if useCtrl or useAdmm:
			pvpc = CurtCtrl("PVController-House-" + str(houseNum), pv, ctrl, sim)
			pvpc.useEventControl = useEC
			pvpc.perfectPredictions = usePP
			pvpc.perfectPredictions = True # Historic data is not correct for the current implementation

			pvpc.commodities = list(pv.commodities)
			pvpc.weights = dict(weights)

		elif useAuction:
			pvpc = CurtAuctionCtrl("PVController-House-" + str(houseNum), pv, ctrl, sim)
			pvpc.strictComfort = not useIslanding
			pvpc.islanding = useIslanding

		elif usePlAuc:
			pvpc = PaCurtCtrl("PVController-House-" + str(houseNum), pv, ctrl, sim)
			pvpc.useEventControl = useEC
			pvpc.perfectPredictions = usePP
			pvpc.perfectPredictions = True # Historic data is not correct for the current implementation
			pvpc.strictComfort = not useIslanding
			pvpc.islanding = useIslanding

		# NOTE: Solar panels connected using a three phase inverter can be modelled as three separate PV panels
		# Use a for loop to instantiate these three panels
		# This "workaround" is required as uncontrollables, of which the PV is inherited, do not support multiple commodities

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

	if not useALPG:
		print("[MODEL] Cannot add an Whitegoods without proper data! Enable ALPG input")

# WASHING MACHINE
	idx = alpg.indexFromFile(alpgFolder+"WashingMachine_Starttimes.txt", houseNum)
	if idx != -1:
		wm = TsDev("WashingMachine-House-"+str(houseNum),  sim) # same name, host
		# Static profile, complex numbers ot reflect reactive power
		wm.profile = [complex(66.229735, 77.4311402954),complex(119.35574, 409.21968),complex(162.44595, 516.545199388),complex(154.744551, 510.671236335),complex(177.089979, 584.413201848),complex(150.90621, 479.851164854),complex(170.08704, 540.84231703),complex(134.23536, 460.23552),complex(331.837935, 783.490514121),complex(2013.922272, 587.393996),complex(2032.267584, 592.744712),complex(2004.263808, 584.576944),complex(2023.32672, 590.13696),complex(2041.49376, 595.43568),complex(2012.8128, 587.0704),complex(2040.140352, 595.040936),complex(1998.124032, 582.786176),complex(2023.459776, 590.175768),complex(1995.309312, 581.965216),complex(2028.096576, 591.528168),complex(1996.161024, 582.213632),complex(552.525687, 931.898925115),complex(147.718924, 487.486021715),complex(137.541888, 490.4949133),complex(155.996288, 534.844416),complex(130.246299, 464.477753392),complex(168.173568, 497.908089133),complex(106.77933, 380.79103735),complex(94.445568, 323.813376),complex(130.56572, 317.819806804),complex(121.9515, 211.226194059),complex(161.905679, 360.175184866),complex(176.990625, 584.085324519),complex(146.33332, 501.71424),complex(173.06086, 593.35152),complex(145.07046, 517.342925379),complex(188.764668, 522.114985698),complex(88.4058, 342.394191108),complex(117.010432, 346.43042482),complex(173.787341, 326.374998375),complex(135.315969, 185.177207573),complex(164.55528, 413.181298415),complex(150.382568, 515.597376),complex(151.517898, 540.335452156),complex(154.275128, 509.122097304),complex(142.072704, 506.652479794),complex(171.58086, 490.815333752),complex(99.13293, 368.167736052),complex(94.5507, 366.193286472),complex(106.020684, 378.085592416),complex(194.79336, 356.012659157),complex(239.327564, 302.865870739),complex(152.75808, 209.046388964),complex(218.58576, 486.26562702),complex(207.109793, 683.481346289),complex(169.5456, 581.2992),complex(215.87571, 712.409677807),complex(186.858018, 573.073382584),complex(199.81808, 534.79864699),complex(108.676568, 403.611655607),complex(99.930348, 356.366544701),complex(151.759998, 358.315027653),complex(286.652289, 300.697988258),complex(292.921008, 266.244164873),complex(300.5829, 265.089200586),complex(296.20425, 261.22759426),complex(195.74251, 216.883021899),complex(100.34136, 260.038063655),complex(312.36975, 275.4842252),complex(287.90921, 261.688800332),complex(85.442292, 140.349851956),complex(44.8647, 109.208529515)]
		wm.timeBase = 60		# NOTE: TimeBase of the dataset
		wm.strictComfort = not useIslanding

		# Add all jobs
		for j in range(0,  len(wm_starttimes[idx])):
			wm.addJob(wm_starttimes[idx][j],  wm_endtimes[idx][j])

		if useMC:
			wm.commodities = [commodities[phase%3]]

		sm.addDevice(wm)

		if useCtrl or useAdmm:
			#add a controller for the Timeshitable
			wmc = TsCtrl("WashingMachineController-House-"+str(houseNum),  wm,  ctrl,  sim) 	# params: name, device, higher-level controller, simHost
			wmc.perfectPredictions = usePP						# Same tricks
			wmc.useEventControl = useEC
			wmc.timeBase = ctrlTimeBase

			wmc.commodities = list(wm.commodities)
			wmc.weights = dict(weights)
		elif useAuction:
			wmc = TsAuctionCtrl("WashingMachineController-House-"+str(houseNum),  wm,  ctrl,  sim) 	# This time: (<name>, <device to be controlled>, <parent controller>, <host>)
			wmc.strictComfort = not useIslanding
			wmc.islanding = useIslanding

		elif usePlAuc:
			wmc = PaTsCtrl("WashingMachineController-House-"+str(houseNum),  wm,  ctrl,  sim)
			wmc.perfectPredictions = usePP						# Same tricks
			wmc.useEventControl = useEC
			wmc.timeBase = ctrlTimeBase
			wmc.strictComfort = not useIslanding
			wmc.islanding = useIslanding

# DISHWASHER
	# Follows the exact same reasoning as the Washing Machine above
	idx = alpg.indexFromFile(alpgFolder+"Dishwasher_Starttimes.txt", houseNum)
	if idx != -1:
		dw = TsDev("DishWasher-House-"+str(houseNum), sim)
		dw.profile =[complex(2.343792, 9.91720178381),complex(0.705584, 8.79153133754),complex(0.078676, 7.86720661017),complex(0.078744, 7.87400627016),complex(0.078948, 7.89440525013),complex(0.079152, 7.91480423011),complex(0.079016, 7.90120491012),complex(0.078812, 7.88080593015),complex(0.941108, 3.10574286964),complex(10.449, 18.0981988883),complex(4.523148, 1.78766247656),complex(34.157214, 15.5624864632),complex(155.116416, 70.6731270362),complex(158.38641, 72.1629803176),complex(158.790988, 67.6446776265),complex(158.318433, 72.1320090814),complex(158.654276, 67.5864385584),complex(131.583375, 109.033724507),complex(13.91745, 13.0299198193),complex(4.489968, 1.91271835851),complex(1693.082112, 669.148867416),complex(3137.819256, 447.115028245),complex(3107.713851, 442.825240368),complex(3120.197256, 444.604029241),complex(3123.464652, 445.069607955),complex(3114.653256, 443.814052026),complex(3121.27497, 444.757595169),complex(3116.305863, 444.04953577),complex(3106.801566, 442.695246796),complex(3117.703743, 444.248722882),complex(3118.851648, 444.412290486),complex(3110.016195, 443.15330662),complex(3104.806122, 442.410911425),complex(1148.154728, 416.724520071),complex(166.342624, 70.8616610914),complex(161.205252, 68.6731497838),complex(160.049824, 68.1809395169),complex(158.772588, 67.6368392593),complex(158.208076, 67.3963581543),complex(157.926096, 67.2762351774),complex(157.01364, 66.8875305491),complex(112.30272, 108.243298437),complex(11.65632, 9.35164905552),complex(17.569056, 18.4299236306),complex(4.947208, 2.10750178285),complex(4.724016, 2.012422389),complex(143.12025, 65.2075123351),complex(161.129536, 68.6408949029),complex(160.671915, 63.501604078),complex(23.764224, 12.8265693277),complex(136.853808, 62.352437012),complex(159.11184, 62.8850229849),complex(159.464682, 63.0244750664),complex(159.04302, 62.8578235805),complex(36.68544, 55.7061505818),complex(9.767628, 7.07164059421),complex(4.902772, 2.08857212612),complex(2239.315008, 885.033921728),complex(3116.846106, 444.126516228),complex(3111.034014, 443.298337972),complex(3118.112712, 444.306997808),complex(3111.809778, 443.408878355),complex(3113.442189, 443.641484325),complex(3110.529708, 443.226478259),complex(3104.676432, 442.392431601),complex(3101.093424, 441.881880613),complex(3121.076178, 444.729268843),complex(1221.232208, 443.248103556),complex(159.964185, 63.2218912841),complex(2663.07828, 966.568347525),complex(272.524675, 436.038267268),complex(7.76832, 5.82624),complex(3.258112, 1.75854256572),complex(3.299408, 1.69033685682),complex(3.295136, 1.68814824631),complex(3.256704, 1.75778260783),complex(3.258112, 1.75854256572),complex(3.262336, 1.7608224394),complex(2224.648744, 807.439674778),complex(367.142872, 587.426961418),complex(4.711025, 11.8288968082)]
		dw.timeBase = 60
		dw.strictComfort = not useIslanding

		for j in range(0,  len(dw_starttimes[idx])):
			dw.addJob(dw_starttimes[idx][j],  dw_endtimes[idx][j])

		if useMC:
			dw.commodities = [commodities[phase%3]]

		sm.addDevice(dw)

		if useCtrl or useAdmm:
			dwc = TsCtrl("DishWasherController-House-"+str(houseNum), dw, ctrl, sim)
			dwc.perfectPredictions = usePP
			dwc.useEventControl = useEC
			dwc.timeBase = ctrlTimeBase
			dwc.weights = dict(weights)
			dwc.commodities = list(dw.commodities)

		elif useAuction:
			dwc = TsAuctionCtrl("DishWasherController-House-"+str(houseNum),  dw,  ctrl,  sim) 	# This time: (<name>, <device to be controlled>, <parent controller>, <host>)
			dwc.strictComfort = not useIslanding
			dwc.islanding = useIslanding

		elif usePlAuc:
			dwc = PaTsCtrl("DishWasherController-House-"+str(houseNum), dw, ctrl, sim)
			dwc.perfectPredictions = usePP						# Same tricks
			dwc.useEventControl = useEC
			dwc.timeBase = ctrlTimeBase
			dwc.strictComfort = not useIslanding
			dwc.islanding = useIslanding

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

# ELECTRIC VEHICLE
	# Add an electric vehicle, for which a buffer-timeshiftable is required
	idx = alpg.indexFromFile(alpgFolder+"ElectricVehicle_Specs.txt", houseNum)
	if not useALPG:
		print("[MODEL] Cannot add an EV without proper data! Enable ALPG input")

	if idx != -1:
		ev = BtsDev("ElectricVehicle-House-"+str(houseNum),  sim)	# params: name, simHost
		#Set the parameters:
		if not useALPG:
			ev.capacity = 100000 			# Tesla Model X maxed out
			ev.chargingPowers = [0, 7400] 	# Up to 32A home charging
		else:
			ev.capacity = ev_specs[idx][0]				# Capacity in Wh
			ev.chargingPowers = [0, ev_specs[idx][1]]	# Charging powers, NOTE: PER PHASE IN N PHASE CHARGING
														# NOTE! For the case where only charging 0 or charging between a min and max bound is allowed, "ev.chargingPowers" must have the form "[0, min, max]". bts.ctr. will automatically use the correct EV algorithm for such inputs
			# ChargingPowers is either:
			# 		- a list of possible states (including 0), if discrete is True
			# 		- or a minimum and maximum (thus 2 values) if discrete is False

		if useMC:
			# Now we use default 3 phase charging
			ev.chargingPowers = [0, 22000/3] # Charging power is given per phase!
			ev.commodities = list(commodities)

		ev.soc = ev.capacity 			# recommended to sync (initial)soc and capacity
		ev.discrete = False				# Use discrete chargingsteps instead?
		ev.strictComfort = not useIslanding


		#  System to add charging jobs
		for j in range(0,  len(ev_energy[idx])):
			if min(ev_energy[idx][j], ev.capacity) > 0:
				ev.addJob(ev_starttimes[idx][j],  ev_endtimes[idx][j],  min(ev_energy[idx][j], ev.capacity))
				# Optionally, another parameter can be provided that specifies the EV type, i.e., ev.addJob(ev_starttimes[idx][j],  ev_endtimes[idx][j],  min(ev_energy[idx][j], ev.capacity), ev_type)

		# Decide between Hybrid PHEV or FEV:
		if ev.capacity < 15000:
			ev.hybrid = True
		else:
			ev.hybrid = False

		sm.addDevice(ev)

		if useCtrl or useAdmm:
			#add a controller for the EV.
			#Note, we need to give it a name, connect it to the EV, connect it to the group controller and finally connect it to the host:
			evc = BtsCtrl("ElectricVehicleController-House-"+str(houseNum),  ev,  ctrl,  sim) 	# params: name, device, higher-level controller, simHost
			#Controller params
			evc.perfectPredictions = usePP
			evc.useEventControl = useEC
			evc.timeBase = ctrlTimeBase
			evc.weights = dict(weights)
			evc.commodities = list(ev.commodities)

		elif useAuction:
			evc = BtsAuctionCtrl("ElectricVehicleController-House-"+str(houseNum),  ev,  ctrl,  sim)
			evc.strictComfort = not useIslanding
			evc.islanding = useIslanding

		elif usePlAuc:
			evc = PaBtsCtrl("ElectricVehicleController-House-"+str(houseNum),  ev,  ctrl,  sim)
			evc.perfectPredictions = usePP
			evc.useEventControl = useEC
			evc.timeBase = ctrlTimeBase
			evc.strictComfort = not useIslanding
			evc.islanding = useIslanding
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

# BATTERY
	#add a battery
	idx = alpg.indexFromFile(alpgFolder+"BatterySettings.txt", houseNum)
	if not useALPG or idx != -1:
		# Follows very much the same reasoning as with the EV above, so the documentation is sparse here
		buf = BufDev("Battery-House-"+str(houseNum), sim, sm)		# params: name, simHost

		#Set the parameter
		if useALPG:
			buf.chargingPowers = [-1*bat_specs[idx][0], bat_specs[idx][0]]
			buf.capacity = bat_specs[idx][1]
			buf.initialSoC = bat_specs[idx][2]
		else:
			# Not using ALPG data
			buf.chargingPowers = [-3700, 3700]
			buf.capacity = 13500
			buf.initialSoC = buf.capacity * 0.5

		buf.soc = buf.initialSoC
		buf.commodities = commodities
		buf.discrete = False

		# Marks to spawn events
		buf.highMark = buf.capacity * 0.8
		buf.lowMark = buf.capacity * 0.2

		buf.strictComfort = not useIslanding

		if useMC:
			if buf.capacity <= 7500:
				buf.commodities = []
				buf.commodities = [(commodities[phase-1])]
			else:
				buf.commodities = ['EL1', 'EL2', 'EL3']

		# add the battery to the smart meter
		sm.addDevice(buf)

		if useFillMethod:
			buf.meter = sm


		# Add a controller
		if useCtrl or useAdmm:
			bufc = BufCtrl("Battery-Controller-House-"+str(houseNum),  buf,  ctrl,  sim) 	# params: name, device, higher-level controller, simHost
			bufc.useEventControl = useEC
			bufc.timeBase = ctrlTimeBase
			bufc.commodities = list(buf.commodities)
			if useMC:
				bufc.weights = dict(weights)
			# Battery reservation options
			bufc.planningCapacity = 1.0 #0.8			# Fraction to use for planning, symmetric (i.e. it uses a Soc ranging from 0+x/2 - 1-x/2, where x is the variable
			bufc.planningPower = 1.0 #0.6			# Fraction of the power to use, as above.
			bufc.eventPlanningCapacity = 1.0	# Fraction to use for planning, symmetric (i.e. it uses a Soc ranging from 0+x/2 - 1-x/2, where x is the variable
			bufc.eventPlanningPower = 1.0		# Fraction of the power to use, as above.

			# Balancing battery
			if useFillMethod:
				buf.parent = ctrl
				buf.balancing = True
			#
			# if useCongestionPoints:
			# 	bufc.congestionPoint = cp

		elif useAuction:
			bufc = BufAuctionCtrl("Battery-Controller-House-"+str(houseNum),  buf,  ctrl,  sim)
			bufc.strictComfort = not useIslanding
			bufc.islanding = useIslanding

		elif usePlAuc:
			bufc = PaBufCtrl("Battery-Controller-House-"+str(houseNum),  buf,  ctrl,  sim)
			bufc.useEventControl = useEC
			bufc.timeBase = ctrlTimeBase
			bufc.strictComfort = not useIslanding
			bufc.islanding = useIslanding


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

# Heating system
	# NOTE: Islanding is not implemented
	# NOTE: No support for threephase connected heatsources
	# NOTE: Only supported with ALPG data at the moment
	idx = alpg.indexFromFile(alpgFolder+"HeatingSettings.txt", houseNum)

	if not useMC:
		elPhase = 'ELECTRICITY'
	else:
		elPhase = commodities[phase - 1]

	zone = ZoneDev2R2C("Zone-House-"+str(houseNum), weather, sun, sim)
	# Zone parameters by R.P. van Leeuwen for heavy semi-detached
	zone.perfectPredictions = usePP
	zone.rFloor = 0.001		# K/W
	zone.rEnvelope = 0.0064	# K/W
	zone.cFloor = 5100 * 3600	# J/K
	zone.cZone = 21100 * 3600	# J/K
	zone.initialTemperature = 18.5

	zone.gainFile = alpgFolder+"Heatgain_Profile.csv"
	zone.ventilationFile = alpgFolder+"Airflow_Profile_Ventilation.csv" # Provides the airflow in M3/h!
	zone.gainColumn =  houseNum
	zone.ventilationColumn = houseNum
	# Add windows to the zone
	zone.addWindow(10, 180)

	# Add a thermostat
	thermostat = Thermostat("Thermostat-House-"+str(houseNum), zone, None, sim)
	thermostat.temperatureSetpointHeating = 18.5 			# setpoint temperature for the zone
	thermostat.temperatureSetpointCooling = 23.0
	thermostat.temperatureMin = 18.5 	# min setpoint temperature for the zone (turn on heating overnight on cold days)
	thermostat.temperatureMax = 23.0 	# max setpoint temperature for the zone (turn on cooling when above)
	thermostat.temperatureDeadband = [-0.1, 0.0, 0.5, 0.6]	# deadband control: [Below heating setpoint (HEAT), Above Heating setpoint (OFF), Below Cooling setpoint (OFF), Above Cooling setpoint (COOL)]
	thermostat.preheatingTime = 3600 			# Preaheating time in seconds before the actual starttime
	thermostat.perfectPredictions = usePP
	thermostat.timeBase = ctrlTimeBase
	# Add the heating schedule
	idx = alpg.indexFromFile(alpgFolder+"Thermostat_Starttimes.txt", houseNum)
	for j in range(0,  len(therm_setpoints[idx])):
		thermostat.addJob(therm_starttimes[idx][j],  therm_setpoints[idx][j])

	# Add a DHW tap
	dhw = DhwDev("DomesticHotWater-House-"+str(houseNum), sim)
	dhw.dhwFile = alpgFolder+"Heatdemand_Profile.csv" # using the weather profile as a quick and dirty test
	dhw.dhwColumn = houseNum
	dhw.perfectPredictions = usePP

	# # add a heat source
	if heat_specs[idx][0] == "CONVENTIONAL": # Gas boiler
		heatsource = GasBoilerDev("GasBoiler-House-"+str(houseNum), sim)
		heatsource.producingTemperatures = [0, 60.0]


	elif heat_specs[idx][0] == "HP":
		heatsource = HeatPumpDev("HeatPump-House-"+str(houseNum), sim)
		heatsource.producingTemperatures = [0, 35.0]
		heatsource.producingPowers = [0, 4500] # use [-4500, 4500] for cooling, but this is unsported yet
		heatsource.commodities = [elPhase, 'HEAT']
		heatsource.cop = {elPhase: 4.0} # Pretty common CoP, each unit of electricity consumed produces 4 units of heat
	else:
		heatsource = CombinedHeatPowerDev("Heatsource-House-"+str(houseNum), sim)
		heatsource.commodities = [elPhase, 'NATGAS', 'HEAT'] # INPUT, OUTPUT
		heatsource.cop = {elPhase: (-13.5/6.0), 'NATGAS': (13.5/21.0)}
	# Look in the sourcecodes of these heating devices to find out about CoP and conversionfactors

	# Define buffer capacity
	heatsource.capacity = 	50000.0
	heatsource.soc = 		25000.0
	heatsource.initialSoC = 25000.0
	heatsource.strictComfort = not useIslanding
	heatsource.islanding = useIslanding

	# Now link the source to the zone, thermostat and dhw
	heatsource.addZone(zone)
	heatsource.addThermostat(thermostat)

	sm.addDevice(heatsource)
	gm.addDevice(heatsource)

	if heat_specs[idx][0] == "CHP" or heat_specs[idx][0] == "HP":
		if useCtrl or useAdmm:
			heatctrl = ThermalBufConvCtrl("HeatController-House-"+str(houseNum),  heatsource,  ctrl,  sim)
			heatctrl.commodities = list(heatsource.commodities)
			if heat_specs[idx][0] == "CHP":
				heatctrl.weights = {elPhase: 1.0, 'NATGAS': 0.0, 'HEAT': 0.0}
			elif heat_specs[idx][0] == "HP":
				heatctrl.weights = {elPhase: 1.0, 'HEAT': 0.0}

			heatctrl.perfectPredictions = usePP
			heatctrl.useEventControl = useEC
			heatctrl.timeBase = ctrlTimeBase
		elif useAuction:
			# Control enabled:
			heatctrl = ThermalBufConvAuctionCtrl("HeatController-House-"+str(houseNum),  heatsource, ctrl,  sim)
			heatctrl.commodities = list(heatsource.commodities)
			if heat_specs[idx][0] == "CHP":
				heatctrl.weights = {elPhase: 1.0, 'NATGAS': 0.0, 'HEAT': 0.0}
			elif heat_specs[idx][0] == "HP":
				heatctrl.weights = {elPhase: 1.0, 'HEAT': 0.0}
			heatctrl.timeBase = ctrlTimeBase
			heatctrl.strictComfort = not useIslanding
			heatctrl.islanding = useIslanding
		elif usePlAuc:
			# Control enabled:
			heatctrl = ThermalPaBufConvCtrl("HeatController-House-"+str(houseNum),  heatsource, ctrl,  sim)
			heatctrl.commodities = list(heatsource.commodities)
			if heat_specs[idx][0] == "CHP":
				heatctrl.weights = {elPhase: 1.0, 'NATGAS': 0.0, 'HEAT': 0.0}
			elif heat_specs[idx][0] == "HP":
				heatctrl.weights = {elPhase: 1.0, 'HEAT': 0.0}
			heatctrl.perfectPredictions = usePP
			heatctrl.useEventControl = useEC
			heatctrl.timeBase = ctrlTimeBase
			heatctrl.strictComfort = not useIslanding
			heatctrl.islanding = useIslanding

	if not heat_specs[idx][0] == "HP":
		heatsource.addDhwTap(dhw)
	else:
		# Heatpump has not enough power to provide tapwater, so we need another to heat water. Note that the generic heatsource is not applicable to planning
		dhwsrc = HeatPumpDev("DomesticHotWaterControllerBoiler-House-"+str(houseNum), sim)
		dhwsrc.producingTemperatures = [0, 60.0]
		dhwsrc.producingPowers = [0, 25000]
		dhwsrc.perfectPredictions = usePP
		dhwsrc.strictComfort = not useIslanding
		dhwsrc.islanding = useIslanding
		dhwsrc.commodities = [elPhase, 'HEAT']
		dhwsrc.cop = {elPhase: 4.0} # Pretty common CoP, each unit of electricity consumed produces 4 units of heat
		dhwsrc.addDhwTap(dhw)

		sm.addDevice(dhwsrc)
		gm.addDevice(dhwsrc)

		if useCtrl or useAdmm:
			dhwctrl = ThermalBufConvCtrl("DomesticHotWaterController-House-"+str(houseNum),  dhwsrc,  ctrl,  sim)
			dhwctrl.commodities = list(dhwsrc.commodities)
			dhwctrl.weights = {elPhase: 1.0, 'HEAT': 0.0}
			dhwctrl.perfectPredictions = usePP
			dhwctrl.useEventControl = useEC
			dhwctrl.timeBase = ctrlTimeBase

		elif useAuction:
			dhwctrl = ThermalBufConvAuctionCtrl("DomesticHotWaterController-House-"+str(houseNum),  dhwsrc,  ctrl,  sim)
			dhwctrl.commodities = list(dhwsrc.commodities)
			dhwctrl.weights = {elPhase: 1.0, 'HEAT': 0.0}
			dhwctrl.timeBase = ctrlTimeBase
			dhwctrl.strictComfort = not useIslanding
			dhwctrl.islanding = useIslanding

		elif usePlAuc:
			dhwctrl = ThermalPaBufConvCtrl("DomesticHotWaterController-House-"+str(houseNum),  dhwsrc,  ctrl,  sim)
			dhwctrl.commodities = list(dhwsrc.commodities)
			dhwctrl.weights = {elPhase: 1.0, 'HEAT': 0.0}
			dhwctrl.perfectPredictions = usePP
			dhwctrl.useEventControl = useEC
			dhwctrl.timeBase = ctrlTimeBase
			dhwctrl.strictComfort = not useIslanding
			dhwctrl.islanding = useIslanding

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

if useCongestionPoints:
	cpstreet = CongestionPoint()
	if useMC:
		for c in commodities:
			cpstreet.setUpperLimit(c,  numOfHouses*500)
			cpstreet.setLowerLimit(c,  -1*numOfHouses*500)
	else:
		cpstreet.setUpperLimit('ELECTRICITY',  numOfHouses*500)
		cpstreet.setLowerLimit('ELECTRICITY',  -1*numOfHouses*500)




# ADD A FLEETCONTROLLER FOR THIS STREET
if useCtrl:
	if useCongestionPoints:
		rootctrl = GroupCtrl("GroupController",  sim, None, cpstreet)
	else:
		rootctrl = GroupCtrl("GroupController",  sim)
	rootctrl.useEventControl = useEC
	rootctrl.minImprovement = 0.001
	rootctrl.planHorizon = 2*int(24*3600/ctrlTimeBase)
	rootctrl.planInterval = int(24*3600/ctrlTimeBase)
	rootctrl.isFleetController = True
	rootctrl.timeBase = ctrlTimeBase
	rootctrl.commodities = list(commodities)
	rootctrl.weights = dict(weights)
	rootctrl.strictComfort = not useIslanding

	if pricesElectricity is not None:
		for c in commodities:
			rootctrl.prices = {}
			rootctrl.prices[c] = pricesElectricity
		rootctrl.profileWeight = profileWeight


elif useAuction:
	# Auctioneer, usually not in the house
	if useCongestionPoints:
		rootctrl = AuctioneerCtrl("Auctioneer",  sim, cpstreet)
	else:
		rootctrl = AuctioneerCtrl("Auctioneer",  sim, None)
	rootctrl.maxGeneration = 0.0    # We try to island here
	rootctrl.minGeneration = 0.0	# Set these two differently, based on an estimated power usage for example
	rootctrl.timeBase = ctrlTimeBase

	rootctrl.strictComfort = not useIslanding
	rootctrl.islanding = useIslanding

elif usePlAuc:
	if useCongestionPoints:
		rootctrl = PaGroupCtrl("GroupController",  sim, None, cpstreet)
	else:
		rootctrl = PaGroupCtrl("GroupController",  sim)
	rootctrl.useEventControl = useEC
	rootctrl.minImprovement = 0.001
	rootctrl.timeBase = ctrlTimeBase
	rootctrl.planHorizon = 2*int(24*3600/ctrlTimeBase)
	rootctrl.planInterval = int(24*3600/ctrlTimeBase)
	rootctrl.isFleetController = True
	rootctrl.timeBase = ctrlTimeBase

	rootctrl.strictComfort = not useIslanding
	rootctrl.islanding = useIslanding

	if pricesElectricity is not None:
		for c in commodities:
			rootctrl.prices = {}
			rootctrl.prices[c] = pricesElectricity
		rootctrl.profileWeight = profileWeight

elif useAdmm:
	if useCongestionPoints:
		rootctrl = AdmmGroupCtrl("GroupController",  sim, None, cpstreet)
	else:
		rootctrl = AdmmGroupCtrl("GroupController",  sim)
	rootctrl.multipleCommits = False	# Allow multiple commits to speedup the optimization
	rootctrl.maxIters = 200 #2.5*numOfHouses
	rootctrl.timeBase = ctrlTimeBase	# 900 is advised hre, must be a multiple of the simulation timeBase
	rootctrl.useEventControl = useEC	# Enable / disable event-based control
	rootctrl.isFleetController = True 	# Very important to set this right in case of large structures. The root controller needs to be a fleetcontroller anyways. See 4.3 of Hoogsteen's thesis
	rootctrl.initialPlan = False 		# Recommended to speed up the process
	rootctrl.strictComfort = True
	rootctrl.planHorizon = 2*int(24*3600/ctrlTimeBase)
	rootctrl.planInterval = int(24*3600/ctrlTimeBase)

	rootctrl.commodities = list(commodities)	# Overwrite the list of commodities
	rootctrl.weights = dict(weights)			# Overwrite the weights
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

# add a household using the previously defined function
for h in range(0, numOfHouses):
	addHouse(None, 0, 0, (h%3), h) # Phase must be: 0 < phase < 4
# For a larger group of houses, use a for loop and change the housenumber (and if applicable the phase).
# Usually it is useful to use the dynamic idx-code as well, and multiple input files.

# The last thing to do is starting the simulation!
sim.startSimulation()
