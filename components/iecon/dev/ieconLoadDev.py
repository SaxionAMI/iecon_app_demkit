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


class IeconLoadDev(LoadDev):

    def __init__(self, host,
                 iecon_scada: MqttSpbEntityScada, iecon_eon_name: str, iecon_eond_name : str,
                 influx=False, reader=None,
                 ):
        LoadDev.__init__(self, iecon_eond_name, host, influx, reader)

        # Save parameters locally
        self._scada = iecon_scada
        self.eon_name = iecon_eon_name
        self.eond_name = iecon_eond_name

        # Update rate:
        self.lastUpdate = -1
        self.updateInterval = 1  # Update every minute

        # InfluxDB extra measurement tags
        self.infuxTagsExtraLog = {
            "spb_eon": iecon_eon_name,
            "spb_eond": iecon_eond_name
        }

        self._data = dict()     # Local storage of device data

        # Subscribe to the device data
        self.device = self._scada.get_edge_node_device(eon_name=self.eon_name,
                                                       eond_name=self.eond_name,
                                                       )
        # To display the data received ( for DEBUG -  Commented on deployment )
        self.device.callback_data = self._spb_dev_data

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
                self.logWarning("%s - IECON EoND is offline, power set to zero." % self.device.entity_domain)

        self.lockState.release()

    # LogStats() is called at the end of a time interval
    # This is your chance to log data
    def logStats(self, time):

        # If there is no data to log, exit inmediately
        if not self._data:
            # print("No data")
            return

        self.lockState.acquire()

        # ---- POWER VALUES ----
        try:
            for c in self.commodities:
                self.logValue("W-power.real.c." + c, self.consumption[c].real)
                if self.host.extendedLogging:
                    self.logValue("W-power.imag.c." + c, self.consumption[c].imag)

                if c in self.plan and len(self.plan[c]) > 0:
                    self.logValue("W-power.plan.real.c." + c, self.plan[c][0][1].real)
                    if self.host.extendedLogging:
                        self.logValue("W-power.plan.imag.c." + c, self.plan[c][0][1].imag)
        except:
            pass

        # ---- OTHER DATA - If enabled ----
        if self.host.extendedLogging:
            try:
                # TODO at the moment it is enforced for commodity ELECTRICITY
                for key in self._data:
                    self.logValue(key + ".ELECTRICITY", self._data[key])

                # for c in self.commodities:
                #     for key in self._data:
                #         self.logValue(key + "." + c, self._data[key])
            except:
                pass

        # Reset data till next iteration, it will be updated automatically when device send data
        self._data = {}

        self.lockState.release()

