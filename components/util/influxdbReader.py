# Copyright 2023 University of Twente
import time

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import requests

from util.reader import Reader
from usrconf import demCfg

class InfluxDBReader(Reader):
	def __init__(self, measurement, address=None, port=None, database=None, timeBase=60, aggregation='mean', offset=None, raw=False, value="W-power.real.c.ELECTRICITY", tags={}, host=None):
		Reader.__init__(self, timeBase, -1, offset, host)

		self.cacheFuture = False # Allow to cache future data. Useful in case of given simulation data

		#params
		self.timeBase = timeBase
		self.offset = offset

		if address is not None and address[0:4] != "http":
			address = "http://" + address

		if address is None:
			self.address = demCfg['db']['influx']['address']
		else:
			self.address = address

		if port is None:
			self.port = demCfg['db']['influx']['port']
		else:
			self.port = port

		if database is None:
			self.database = demCfg['db']['influx']['dbname']
		else:
			self.database = database

		self.token = demCfg["db"]["influx"].get("token")  # If using InfluxDB 2x, we need token access

		self.user = ""
		self.password = ""
		self.prefix = ""

		self.measurement = measurement
		self.aggregation = aggregation
		self.raw = raw

		self.value = value
		self.tags = tags

		# self.host.logDebug(
		# 	"[influxDbReader].init() - " + self.database
		# 	+ " - " + self.measurement
		# 	+ " - " + self.aggregation
		# 	+ " - " + self.value
		# 	+ " - " + str(self.tags)
		# )

	def retrieveValues(self, startTime, endTime=None, value=None, tags=None):
		if endTime is None:
			endTime = startTime + self.timeBase
		if value is None:
			value = self.value
		if tags is None:
			tags = self.tags

		# Create a string from the tags to put in the query
		condition = ""
		if tags:
			for tag_key, tag_value in tags.items():
				condition += '(\"' + tag_key + '\" = \'' + tag_value + '\') AND '

		query = 'SELECT ' + self.aggregation + '(\"' + value + '\") FROM \"' + self.measurement + '\" WHERE ' + condition + 'time >= ' + str(
			startTime) + '000000000 AND time < ' + str(endTime) + '000000000 GROUP BY time(' + str(
			self.timeBase) + 's) fill(previous) ORDER BY time ASC'  # LIMIT '+str(l)

		self.host.logDebug("[influxdbReader].retrieveValues() - %s" % str(query))

		r = self.getData(query, startTime, endTime)

		return r

	def getData(self, query, startTime, endTime):

		url = self.address + ":" + str(self.port) + "/query"

		if not url.startswith("http"):
			url = "http://" + url

		payload = {}
		payload['db'] = self.database
		payload['q'] = query
		if not self.token:
			payload['u'] = self.user
			payload['p'] = self.password

		headers = None
		if self.token:
			headers = {
				'Authorization': f'Token {self.token}',
			}

		r = requests.post(url, params=payload, headers=headers)

		if self.raw:
			return r.json()
		else:
			result = [None] * int((endTime - startTime) / self.timeBase)
			try:
				if('series' in r.json()['results'][0]):
					idx = 0
					d = r.json()['results'][0]['series'][0]['values']
					for value in d:
						result[idx] = value[1]
						idx += 1
			except Exception as e:
				self.host.logDebug("[influxdbReader].getData() exception - " + str(e))
				pass

			return result