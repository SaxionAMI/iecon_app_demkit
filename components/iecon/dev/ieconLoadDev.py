# Copyright 2024 Saxion University of Applied Sciences

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dev.loadDev import LoadDev

from mqtt_spb_wrapper import MqttSpbEntityScada
from iecon.dev.tools.ieconDevTools import iecon_parse_spb_data_2_demkit
from iecon.database.ieconInfluxDB import IeconInfluxDBReader


class IeconLoadDev(LoadDev):

    def __init__(self, host,
                 iecon_scada: MqttSpbEntityScada,
                 eon_name: str,
                 eond_name : str,
                 influx=False,
                 ):

        # Initialize parent class
        LoadDev.__init__(self, eond_name + "-dev", host, influx)

        # Save parameters locally
        self._scada = iecon_scada
        self.eon_name = eon_name
        self.eond_name = eond_name

        # Update rate:
        self.lastUpdate = -1
        self.updateInterval = 1  # Update every minute

        self._data = dict()     # Local storage of device data

        # REALTIME DATA BUFFER - Temp buffer for data
        self._temp_data_pow = []  # Array to store the device real time data points
        self._last_pow_avg = 0  # Last calculated average - LOQIO IX FILTER
        self._last_pow_timestamp = 0  # Last calculated average timestamp
        self._TIMEOUT_NODATA = 300  # Timeout value if no data is received, avg value will be zeroed

        # Subscribe to the device data
        self.device = self._scada.get_edge_device(
            eon_name=self.eon_name,
            eond_name=self.eond_name,
        )

        # InfluxDB extra measurement tags -------------------------------------------------------------------
        self.log_db_tags_extra = {"EON": self.eon_name, "EOND": self.eond_name}
        self.log_db_tags_extra["ETYPE"] = "demkit-dev"
        if self.device.attributes.get_value("CTYPE"):
            self.log_db_tags_extra["CTYPE"] = self.device.attributes.get_value("CTYPE")
        if self.device.attributes.get_value("CTYPEC"):
            self.log_db_tags_extra["CTYPEC"] = self.device.attributes.get_value("CTYPEC")

        # If using IECON InfluxDB, use specific IECON InfluxDB readers
        if self.host.db.__class__.__name__ == "IeconInfluxDB":
            self.reader = IeconInfluxDBReader(host=host, db_measurement=eon_name, entity_name=eond_name, commodity="electricity")
            self.readerReactive = IeconInfluxDBReader(host=host, db_measurement=eon_name, entity_name=eond_name, field_name="POW_REAC", commodity="electricity")  # Reactive power (imaginary)

        # Set DATA POW callback to receive the values. We store them in the list and calculate the average
        self.device.data["POW"].callback_on_change = self._callback_data_pow

    def _callback_data_pow(self, data):
        """
        Callback executed everytime that a POW value is received.
        Args:
            data: current pow value

        Returns:
        """

        # Store the data into the temp list
        self._temp_data_pow.append(data)

    def preTick(self, time, deltatime=0):

        # We should not be a bad citizen to the service
        self.lockState.acquire()
        if (self.host.time() - self.lastUpdate) > self.updateInterval:

            # Check if data has been received - Calculate average
            if len(self._temp_data_pow) > 0:
                self._last_pow_avg = (float(sum(self._temp_data_pow)) /
                                      len(self._temp_data_pow))
                self._last_pow_timestamp = time

                # self.host.logDebug("POW: %.3f - %f - %d" % (
                # self._last_pow_avg, self._last_pow_timestamp, len(self._temp_data_pow)))

                self._temp_data_pow = []  # Reset the values

            # Check if the data point it is too old, then zeroed
            if time > (self._last_pow_timestamp + self._TIMEOUT_NODATA):
                self._last_pow_avg = 0  # Clear the value

            # Update consumption
            self.consumption['ELECTRICITY'] = complex(self._last_pow_avg, 0.0)

            # If all succeeded:
            self.lastUpdate = self.host.time()

        self.lockState.release()

    # LogStats() is called at the end of a time interval
    # This is your chance to log data
    def logStats(self, time):

        self.lockState.acquire()
        for c in self.commodities:
            self.logValue('POW', self.consumption[c].real, tags={"CTYPE": c.lower()})  # 'W-power.real.c.'+c
            self.logValue('ENE', self.consumption[c].real / (3600.0 / self.timeBase),
                          tags={"CTYPE": c.lower()})  # 'Wh-energy.c.'+c
            if self.host.extendedLogging:
                self.logValue("POW_REAC", self.consumption[c].imag, tags={"CTYPE": c.lower()})  # "W-power.imag.c."+c

        self.lockState.release()

        # # RAW device data is being stored automatically by the IECON framework
        # # We don't need to store any extra data for this device
        # return
