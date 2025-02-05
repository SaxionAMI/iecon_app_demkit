# Copyright 2023 University of Twente, Saxion UAS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ctrl.live.livePvCtrl import LivePvCtrl
import time

class IeconLivePvCtrl(LivePvCtrl):

	def __init__(self,  name,  dev, ctrl, sun, host):

		name += "-ems-ctrl"		# Add postfix to identify demkit compnents

		# Parent initialization
		LivePvCtrl.__init__(self,  name,  dev, ctrl, sun, host)

		# InfluxDB tags - IECON-based extra tags
		self.log_db_tags_extra["EON"] = self.dev.eon_name  # Edge entity
		self.log_db_tags_extra["EOND"] = self.name  # Device name - In this case the EMS Controller entity
		self.log_db_tags_extra["ETYPE"] = "demkit-dctrl"  # Entity type

		# IECON - Inherit the CTYPE and CTYPEC from self.dev
		if "CTYPE" in dev.log_db_tags_extra.keys():
			self.log_db_tags_extra["CTYPE"] = dev.log_db_tags_extra.get("CTYPE")
		if "CTYPEC" in dev.log_db_tags_extra.keys():
			self.log_db_tags_extra["CTYPEC"] = dev.log_db_tags_extra.get("CTYPEC")

	# Override base method to enable the backup of planning ( predictions ) into the DB
	def endSynchronizedPlanning(self, signal):
		"""
			Overwrite base method to allow to store the final planning on the device.
		Args:
			signal:
		Returns:

		"""

		# Call parent method
		result = LivePvCtrl.endSynchronizedPlanning(self, signal)

		# IECON DB data point definitions
		db_measurement = self.dev.eon_name		# Save it as part of the Edge/EoN/Home list of devices
		db_tags = {
			"ENAME": "forec-" + self.dev.eond_name, 	# Virtual Device (EoND) to store this data.
			"ETYPE": "forecast-ele",			# Forecast service
			"ESTYPE": self.dev.eond_name,    	# Name of the device for the forecast data
		}

		# Inherit other IECON tags from device
		if "CTYPE" in self.dev.log_db_tags_extra.keys():
			db_tags["CTYPE"] = self.dev.log_db_tags_extra["CTYPE"]
		if "CTYPEC" in self.dev.log_db_tags_extra.keys():
			db_tags["CTYPEC"] = self.dev.log_db_tags_extra["CTYPEC"]

		self.logDebug("IeconLivePvCtrl - Saving planning / forecasting - % s - %s" % (self.name, str(db_tags)))

		# Save the data into the DB - We use this direct method to inject data directly using the IECON format.
		self.host.db.appendValue(
			measurement=db_measurement,
			values={"forecast.event": 1},
			time=time.time(),
			tags=db_tags
		)

		# Save the planning for the device in the database.
		for c in signal.commodities:

			for i in range(0, signal.planHorizon):

			# 	self.dev.logValue("forecast.POW", self.plan[c][].real, int(signal.time + i * signal.timeBase))
			# 	if self.host.extendedLogging:
			# 		self.dev.logValue("forecast.POW_REAC", self.plan[c][int(signal.time + i * signal.timeBase)].imag, int(signal.time + i * signal.timeBase))

				ts = int(signal.time + i * signal.timeBase)	 # Current timestamp

				# Save the data into the DB - We use this direct method to inject data directly using the IECON format.
				self.host.db.appendValue(
					measurement=db_measurement,
					time=ts,
					values={"forecast.POW": self.plan[c][ts].real},
					tags=db_tags
				)

				if self.host.extendedLogging:
					self.host.db.appendValue(
						measurement=db_measurement,
						time=ts,
						values={"forecast.POW_REAC": self.plan[c][ts].imag},
						tags=db_tags
					)

		# Return the parent method results
		return result

