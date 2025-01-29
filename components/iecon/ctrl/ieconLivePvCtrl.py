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

class IeconLivePvCtrl(LivePvCtrl):

	def __init__(self,  name,  dev, ctrl, sun, host):

		name += "-ems-ctrl"		# Add postfix to identify demkit compnents

		# Parent initialization
		LivePvCtrl.__init__(self,  name,  dev, ctrl, sun, host)

		# InfluxDB  -------------------------------------------------------------------
		self.log_db_tags_extra["EON"] = dev.eon_name  # Edge entity
		self.log_db_tags_extra["EOND"] = name  # Device name - In this case the EMS Controller entity
		self.log_db_tags_extra["ETYPE"] = "forecast-provider"  # Entity type
		self.log_db_tags_extra["ESTYPE"] = dev.eond_name  # Entity SubType - In this case the device name

		# Copy some DEV tags, if existing
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

		self.logDebug("IeconLivePvCtrl - Saving planning - " + self.name)

		# Call parent method
		result = LivePvCtrl.endSynchronizedPlanning(self, signal)

		#
		# # Debug - log when predictions have been generated
		# self.dev.logValue("forecast.event", 1)
		#
		# # Save the planning for the device in the database.
		# for c in signal.commodities:
		# 	for i in range(0, signal.planHorizon):
		# 		self.dev.logValue("forecast.POW", self.plan[c][int(signal.time + i * signal.timeBase)].real, int(signal.time + i * signal.timeBase))
		# 		if self.host.extendedLogging:
		# 			self.dev.logValue("forecast.POW_REAC", self.plan[c][int(signal.time + i * signal.timeBase)].imag, int(signal.time + i * signal.timeBase))

		# Return the parent method results
		return result