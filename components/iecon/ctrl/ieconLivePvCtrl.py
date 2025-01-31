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

		# InfluxDB tags - IECON-based extra tags
		self.log_db_tags_extra["EON"] = self.dev.eon_name  # Edge entity
		self.log_db_tags_extra["EOND"] = self.name  # Device name - In this case the EMS Controller entity
		self.log_db_tags_extra["ETYPE"] = "demkit-dctrl"  # Entity type

		# IECON - Inherit the CTYPE and CTYPEC from self.dev
		if "CTYPE" in dev.log_db_tags_extra.keys():
			self.log_db_tags_extra["CTYPE"] = dev.log_db_tags_extra.get("CTYPE")
		if "CTYPEC" in dev.log_db_tags_extra.keys():
			self.log_db_tags_extra["CTYPEC"] = dev.log_db_tags_extra.get("CTYPEC")