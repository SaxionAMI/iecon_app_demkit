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

import requests
from pprint import pprint
from dev.loadDev import LoadDev
from dev.iecon import MqttSpbEntityScada
from dev.iecon.ieconTools import iecon_parse_spb_data_2_demkit


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
        self.infuxTags = {"spb_eon": iecon_eon_name,
                          "spb_eond": iecon_eond_name}

        self._data = dict()     # Local storage of device data

        # Subscribe to the device data
        self.device = self._scada.get_edge_node_device(eon_name=self.eon_name,
                                                       eond_name=self.eond_name,
                                                       )
        # To display the data received ( for DEBUG -  Commented on deployment )
        self.device.callback_data = self._spb_dev_data

    # Fixme make async
    def preTick(self, time, deltatime=0):

        # We should not be a bad citizen to the service
        self.lockState.acquire()
        if (self.host.time() - self.lastUpdate) > self.updateInterval:

            if self.device.is_alive():

                # Get the data from the device
                # This will retrieve the last value received. You can get the timestamp
                value = float(self.device.data.get_value("POW")) * self.scaling

                # Now, value contains the power production by the pv setup, now we can set it as consumption:
                for c in self.commodities:
                    self.consumption[c] = complex(value / len(self.commodities), 0.0)

                # If all succeeded:
                self.lastUpdate = self.host.time()
            else:
                self.logWarning("%s - IECON EoND is offline, data ignored" % self.device.entity_domain)

        self.lockState.release()

    # IECON Device DATA callback - Real time data messages from the device
    def _spb_dev_data(self, msg):

        # self.logMsg("%s - DATA received - %s" % (self.device.spb_eon_name, msg))

        # Convert the spB data message into demkit format and update the values in _data
        self._data.update(iecon_parse_spb_data_2_demkit(msg))

        pass

    # LogStats() is called at the end of a time interval
    # This is your chance to log data
    def logStats(self, time):

        # If there is no data to log, exit inmediately
        if not self._data:
            # print("No data")
            return

        self.lockState.acquire()

        # POWER VALUES
        try:
            for c in self.commodities:
                self.logValue("W-power.real.c." + c, self.consumption[c].real)
                self.logValue("W-power.imag.c." + c, self.consumption[c].imag)
                if c in self.plan and len(self.plan[c]) > 0:
                    self.logValue("W-power.plan.real.c." + c, self.plan[c][0][1].real)
                    self.logValue("W-power.plan.imag.c." + c, self.plan[c][0][1].imag)
        except:
            pass

        # OTHER DATA
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

