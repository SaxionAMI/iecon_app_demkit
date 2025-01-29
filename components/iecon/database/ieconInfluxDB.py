# Copyright 2023 University of Twente, 2024 Saxion UAS, Javier FG
import datetime
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time as tm
from usrconf import demCfg
from database.influxDB import InfluxDB
from util.reader import Reader
import requests


class IeconInfluxDB(InfluxDB):

    def __init__(self, host):

        super().__init__(host)  # Initialize the upper class

        # InfluxDB specific modifications
        self.database               = demCfg.get("IECON_SPB_DOMAIN_ID", "IECON")  # Get the domain
        self.database_measurement   = "ems-demkit-" + self.database  # Default DB bucket measurement name - Entity data will be stored here.

        # Host update
        self.host.log_db_measurement = self.database_measurement     # Update the default bucket measurement

        self.host.logDebug("[IeconInfluxDB.init] " + self.database)

    def appendValue(self, measurement, tags, values, time, deltatime=0):

        # create tags
        tagstr = ""
        for key, value in tags.items():
            if not tagstr == "":
                tagstr += ","
            tagstr += key + "=" + value

        # create vals
        valsstr = ""
        for key, value in values.items():
            if not valsstr == "":
                valsstr += ","
            valsstr += key + "=" + str(value)

        # Check the time
        timestr = str(int(time * 1000000000.0) + (deltatime * 1000))
        if self.useSysTime:
            time = str(tm.time())
            timestr = time.replace('.', '')
            timestr += "000"

        s = self.prefix + measurement + ","
        s += tagstr + " "
        s += valsstr + " "
        s += timestr
        s += '\n'

        # self.host.logDebug("[InfluxDB.appendValue        ] " + s.rstrip("\n"))

        self.data.append(s)

    def appendValuePrepared(self, data, time, deltatime=0):

        # -- DEMKIT CODE ----------------------------------------------

        timestr = str(int(time * 1000000000.0) + (deltatime * 1000))
        if self.useSysTime:
            time = str(tm.time())
            timestr = time.replace('.', '')
            timestr += "000"
        db_data_line = "%s%s %s" % (self.prefix, data, timestr)

        # self.host.logDebug("[InfluxDB.appendValuePrepared] " + db_data_line)

        self.data.append(db_data_line)


class IeconInfluxDBReader(Reader):
    """
    InfluxDB Reader class to get data directly from IECON formated InfluxDB database
    """

    def __init__(
            self,
            host,
            db_measurement: str,
            entity_name: str,
            field_name="POW",
            commodity=None,
            aggregation="mean",
            offset=None,
            raw=False,
            db: IeconInfluxDB=None,
    ):
        """

        Args:
            host: Simulation host
            db: database
            db_measurement:
            entity_name:
            field_name:
            commodity:
            aggregation:
            offset:
            raw:

        """

        # def __init__(self, measurement, address=None, port=None, database=None, timeBase=60, aggregation='mean', offset=None, raw=False, value="W-power.real.c.ELECTRICITY", tags={}, host=None):

        Reader.__init__(self, host.timeBase, -1, offset, host)

        self.cacheFuture = False  # Allow to cache future data. Useful in case of given simulation data

        # params
        if not db:
            self.db = host.db
        else:
            self.db = db

        self.db_measurement = db_measurement
        self.entity_name = entity_name
        self.entity_commodity = commodity

        self.field_name = field_name

        self.timeBase = host.timeBase
        self.offset = offset

        self.aggregation = aggregation

        self.raw = raw


    def retrieveValues(self, startTime, endTime=None, field_name=None, tags=None):

        if endTime is None:
            endTime = startTime + self.timeBase
        if field_name is None:
            field_name = self.field_name

        # Condition query
        condition = ' (\"ENAME\" = \'' + self.entity_name + '\') AND '
        if self.entity_commodity:
            condition += '(\"CTYPE\" = \'' + self.entity_commodity + '\') AND '

        query = 'SELECT ' + self.aggregation + '(\"' + field_name + '\") FROM \"' + self.db_measurement + '\"' \
                + ' WHERE ' + condition \
                + 'time >= ' + str(startTime) + '000000000 AND time < ' + str(endTime) + '000000000' \
                + ' GROUP BY time(' + str(self.timeBase) + 's) fill(previous) ORDER BY time ASC'  # LIMIT '+str(l)

        self.host.logDebug("[IeconInfluxdbReader].retrieveValues: %s _ %s , %s , %s" % (
            datetime.datetime.fromtimestamp(startTime).isoformat(),
            datetime.datetime.fromtimestamp(endTime).isoformat(),
            self.db.database,
            str(query))
        )

        try:
            r = self.getData(query, startTime, endTime)
        except Exception as e:
            self.host.logWarning("[IeconInfluxdbReader.retrieveValues] exception <%s> - payload: %s" % (str(e), query))

        return r

    def getData(self, query, startTime, endTime):

        url = self.db.address + ":" + str(self.db.port) + "/query"
        req = None

        if not url.startswith("http"):
            url = "http://" + url

        payload = dict()

        payload['db'] = self.db.database
        payload['q'] = query
        if not self.db.token:
            payload['u'] = self.db.username
            payload['p'] = self.db.password

        headers = None
        if self.db.token:
            headers = {
                'Authorization': f'Token {self.db.token}',
            }

        try:
            req = requests.post(url, params=payload, headers=headers)
        except Exception as e:
            self.host.logWarning("[IeconInfluxdbReader.getData] exception <%s> - payload: %s" % (str(e), payload))

        if self.raw:
            return req.json()
        else:
            result = [None] * int((endTime - startTime) / self.timeBase)
            try:
                if ('series' in req.json()['results'][0]):
                    idx = 0
                    d = req.json()['results'][0]['series'][0]['values']
                    for value in d:
                        result[idx] = value[1]
                        idx += 1
            except Exception as e:
                self.host.logDebug("[influxdbReader].getData() exception - " + str(e))
                pass

            return result
