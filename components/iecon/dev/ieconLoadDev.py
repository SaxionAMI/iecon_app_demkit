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

from iecon.dev.mqtt_spb_wrapper.mqtt_spb_entity_scada import MqttSpbEntityScada
from iecon.dev.tools.ieconDevTools import iecon_parse_spb_data_2_demkit
from iecon.database.ieconInfluxDB import IeconInfluxDBReader


class IeconLoadDev(LoadDev):

    def __init__(self, host,
                 iecon_scada: MqttSpbEntityScada, eon_name: str, eond_name : str,
                 influx=False,
                 ):

        # Initialize parent class
        LoadDev.__init__(self, eond_name, host, influx)

        # Save parameters locally
        self._scada = iecon_scada
        self.eon_name = eon_name
        self.eond_name = eond_name

        # Update rate:
        self.lastUpdate = -1
        self.updateInterval = 1  # Update every minute

        # InfluxDB extra measurement tags
        self.infuxTagsExtraLog = {
            "spb_eon": eon_name,
            "spb_eond": eond_name
        }

        self._data = dict()     # Local storage of device data

        # Subscribe to the device data
        self.device = self._scada.get_edge_node_device(eon_name=self.eon_name,
                                                       eond_name=self.eond_name,
                                                       )
        # To display the data received ( for DEBUG -  Commented on deployment )
        self.device.callback_data = self._spb_dev_data

        # If using IECON InfluxDB, use specific IECON InfluxDB readers
        if self.host.db.__class__.__name__ == "IeconInfluxDB":
            self.reader = IeconInfluxDBReader(host=host, eon_name=eon_name, eond_name=eond_name, commodity="electricity")
            self.readerReactive = IeconInfluxDBReader(host=host, eon_name=eon_name, eond_name=eond_name, field_name="POW_REAC", commodity="electricity")  # Reactive power (imaginary)


    # IECON Device DATA callback - Real time data messages from the device
    def _spb_dev_data(self, msg: dict):
        """
        Device callback on new data

        This function is called everytime that the device sends data

        Example of msg data:

        {"timestamp":"1727187928026","metrics":[{"name":"POW","timestamp":"1727187928026","datatype":10,"doubleValue":117.5999984741211,"value":117.5999984741211},{"name":"POW_APP","timestamp":"1727187928026","datatype":10,"doubleValue":197.10000610351562,"value":197.10000610351562},{"name":"POW_REAC","timestamp":"1727187928026","datatype":10,"doubleValue":-158.1999969482422,"value":-158.1999969482422},{"name":"CURR","timestamp":"1727187928026","datatype":10,"doubleValue":0.8579999804496765,"value":0.8579999804496765}],"seq":"79"}

        Args:
            msg: spB data message dictionary

        Returns:

        """

        # self.logMsg("%s - DATA received - %s" % (self.device.spb_eon_name, msg))

        # Convert the spB data message into demkit format and update the values in _data
        self._data.update(iecon_parse_spb_data_2_demkit(msg))

        pass

    # Fixme make async
    def preTick(self, time, deltatime=0):

        # We should not be a bad citizen to the service
        self.lockState.acquire()
        if (self.host.time() - self.lastUpdate) > self.updateInterval:

            # Check if device is online
            if self.device.is_alive():

                # Get the data from the device
                # NOTE: the value returned is the last one. You can check timestamp property to validate value.
                value = float(self.device.data.get_value("POW"))

                # Update consumption.
                self.consumption['ELECTRICITY'] = complex(value, 0.0)

                # If all succeeded:
                self.lastUpdate = self.host.time()
            else:
                # TODO - Any action if device is disconnected?
                self.consumption['ELECTRICITY'] = complex(0.0, 0.0)
                # self.logWarning("%s - IECON EoND is offline, power set to zero." % self.device.entity_name)

        self.lockState.release()

    # LogStats() is called at the end of a time interval
    # This is your chance to log data
    def logStats(self, time):

        # We don't need to store any extra data for this device
        # RAW device data is being stored automatically by the IECON framework
        return
