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

        self.spb_domain = demCfg.get("IECON_SPB_DOMAIN_ID", "IECON")  # Get the domain
        self.database = self.spb_domain		# spB IECON database is equal to spB Domain

        # spB EoN identification for DEMKIT
        self.eon_name = "emsDemkit-" + self.spb_domain

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

        # self.host.logDebug("[InfluxDB.appendValue] " + s)

        # -- IECON influxdb data format Conversion ----------------------------------------------
        s = self._db_demkit_data_2_iecon(s)  # convert data
        # self.host.logDebug("    " + s)

        self.data.append(s)

    def appendValuePrepared(self, data, time, deltatime=0):

        # -- DEMKIT CODE ----------------------------------------------

        timestr = str(int(time * 1000000000.0) + (deltatime * 1000))
        if self.useSysTime:
            time = str(tm.time())
            timestr = time.replace('.', '')
            timestr += "000"
        db_data_line = "%s%s %s" % (self.prefix, data, timestr)

        # self.host.logDebug("[InfluxDB.appendValuePrepared] " + dataToBeAdded)

        # -- IECON influxdb data format Conversion ----------------------------------------------
        db_data_line = self._db_demkit_data_2_iecon(db_data_line)     # convert data
        # self.host.logDebug("[InfluxDB.appendValuePrepared] " + db_data_line)

        self.data.append(db_data_line)

    def _db_demkit_data_2_iecon(self, data_line: str) -> str:
        """
        Convert an Influxdb data line in Demkit format, to IECON structure

        Line example:
        controllers,ctrltype=LoadCtrl,name=loadctrl-totaalverbruik-16eda211b788 W-power.realized.imag.c.ELECTRICITY=0.0 1727641800012000000

        Args:
            data_line: input data line demkit

        Returns: influxdb iecon data line converted
        """

        try:

            fields = data_line.split(" ")

            time = fields[2]  # Time value

            # Extract tags
            tags = dict()
            for index, item in enumerate(fields[0].split(",")):

                if index == 0:  # We skip first item
                    continue

                key, value = item.split("=")

                # __type ( ctrltype, devtype, ... ) conversion to ETYPE and ETYPEC
                if key.endswith("type"):
                    tags["ETYPEC"] = key.replace("type", "")
                    value = "demkit-" + value.lower()
                    key = "ETYPE"

                tags[key] = value

            # CHECK NAME must be included as tags, otherwise we do not send the line
            if "name" not in tags.keys():
                self.host.logWarning("[IeconInfluxDB._db_demkit_data_2_iecon] Missing name? " + str(data_line))
                return ""

            # FIELD NAME modifications ------------------------------
            field_name, field_value = fields[1].split("=")

            # Extract commodity from name ( if present )
            if ".c." in field_name:
                field_name, commmodity = field_name.split(".c.")
                tags["CTYPE"] = commmodity.lower()     # Save it into lower

            # FIELD NAME Convert data to IECON format
            if True:

                # FIELD NAME .plan - remove and prefix
                if ".plan" in field_name:
                    field_name = "plan." + field_name.replace(".plan", "")
                # FIELD NAME .realized - remove and prefix
                if ".realized" in field_name:
                    field_name = "realized." + field_name.replace(".realized", "")

                field_name = field_name.replace("W-power.real", "POW")
                field_name = field_name.replace("W-power.imag", "POW_REAC")
                field_name = field_name.replace("Wh-energy.imag", "ENE")
                # field_name = field_name.replace("Wm2-irradiation.GHI", "GHI")  # for now use the original ones, otherwise we need to modify original code
                # field_name = field_name.replace("Wm2-irradiation.DNI", "DNI")
                # field_name = field_name.replace("Wm2-irradiation.DHI", "DHI")

            # ENAME - Entity name from "name"
            tags["ENAME"] = tags["name"]
            tags.pop("name")

            # Generate tag str
            tags_str = ""
            for k, v in tags.items():
                tags_str += ",%s=%s" % (k, v)

            # TODO if tags contain spb_eon and spb_eond data belongs to an spb entity, we should inject the values in the entity measurement=spb_eon, ENAME=spb_eond

            # Generate the InfluxDB data point IECON format
            res = "%s%s %s=%s %s" % (self.eon_name, tags_str, field_name, field_value, time)

            return res

        except Exception as e:
            self.host.logError("[IeconInfluxDB._db_demkit_data_2_iecon] exception " + str(e))
            return ""


class IeconInfluxDBReader(Reader):
    """
    InfluxDB Reader class to get data directly from IECON formated InfluxDB database
    """

    def __init__(
            self,
            host,
            eon_name: str,
            eond_name: str,
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
            eon_name:
            eond_name:
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

        self.eon_name = eon_name
        self.eond_name = eond_name
        self.eond_commodity = commodity

        self.field_name = field_name

        self.timeBase = host.timeBase
        self.offset = offset

        self.aggregation = aggregation

        self.raw = raw

        self.field_name = field_name

    def retrieveValues(self, startTime, endTime=None, field_name=None, tags=None):

        if endTime is None:
            endTime = startTime + self.timeBase
        if field_name is None:
            field_name = self.field_name

        # Condition query
        condition = ' (\"ENAME\" = \'' + self.eond_name + '\') AND '
        if self.eond_commodity:
            condition += '(\"CTYPE\" = \'' + self.eond_commodity + '\') AND '

        query = 'SELECT ' + self.aggregation + '(\"' + field_name + '\") FROM \"' + self.eon_name + '\"' \
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
