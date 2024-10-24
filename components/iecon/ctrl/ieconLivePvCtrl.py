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

		# Parent initialization
		LivePvCtrl.__init__(self,  name,  dev, ctrl, sun, host)

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

		self.logDebug("IeconLivePvCtrl - Saving planning - " + self.name)

		# Debug - log when predictions have been generated
		self.dev.logValue("forecast.event", 1)

		# Save the planning for the device in the database.
		for c in signal.commodities:
			for i in range(0, signal.planHorizon):
				self.dev.logValue("forecast.POW", self.plan[c][int(signal.time + i * signal.timeBase)].real, int(signal.time + i * signal.timeBase))
				if self.host.extendedLogging:
					self.dev.logValue("forecast.POW_REAC", self.plan[c][int(signal.time + i * signal.timeBase)].imag, int(signal.time + i * signal.timeBase))

		# Return the parent method results
		return result