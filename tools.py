import os
import uuid
from ruamel.yaml import YAML


class AppConfig:

    def __init__(self, config_file_path="config.yml"):
        """
            Load application configuration from YAML file

        :param config_file_path:     Path to YAML file ( default: config.yml )
        """

        self._parser = YAML()

        self.file_path = config_file_path

        self._data_load()   # Get the file data

        # ----- Parse configuration values -----------
        self.update_rate = self._get_value(self._data, "UPDATE_RATE", 3)
        self.max_value = self._get_value(self._data, "MAX_VALUE", 1000)

        # IECON related
        self.host_id = self._get_value(self._data, "IECON_HOST_UID", str(uuid.getnode())[-8:])

        self.debug_enabled = self._get_value(self._data, "APP_DEBUG", False)

        self.mqtt_host = self._get_value(self._data, "IECON_MQTT_HOST", "localhost")
        self.mqtt_port = self._get_value(self._data, "IECON_MQTT_PORT", 1883)
        self.mqtt_user = self._get_value(self._data, "IECON_MQTT_USER", "")
        self.mqtt_key = self._get_value(self._data, "IECON_MQTT_PASS", "")

        self.spb_group = self._get_value(self._data, "IECON_SPB_GROUP_ID", "IECON")
        self.spb_edge = self._get_value(self._data, "IECON_SPB_EON_ID", "IECON")

    def _data_load(self):
        """
        Load the YML data from the file
        :return: boolean - Load result
        """
        try:
            with open(self.file_path) as fr:
                self._data = self._parser.load(fr)
            return True
        except:
            self._data = {}
            return False

    def _data_save(self):
        """
        Save the YML data to the file
        :return: boolean - Load result
        """
        try:
            with open(self.file_path, 'w') as fw:
                self._parser.dump(self._data, fw)
            return True
        except:
            return False

    def _data_uncomment_parameter(self, key):
        """
        Function to uncomment a parameter from the yml file

        :return:  boolean - Parameter uncommented result
        """
        commented_key = "#" + key
        output = ""
        founded = False

        with open(self.file_path) as fr:
            for line in fr:

                # Clean line and search for comment
                search = line.replace(" ", "")

                if commented_key in search:
                    output += line[1:]  # remove first character Save the original
                    founded = True
                else:
                    output += line  # Save the original

        if founded:
            with open(self.file_path, "w") as fw:
                fw.write(output)

            self._data_load()   # Reload data from file

        return founded

    @staticmethod
    def _get_value(values, key, default):
        """
        Try to get the config value from the <values> dictionary ( config.yml ).
        If the value is not present in <values> dictionary, the key will be used to search on system environment
        variables. If key not found at all, default value will be returned.

        :param values:      Dictionary containing the configuration values ( from config.yml )
        :param key:         Parameter key name used to find the value
        :param default:     Default parameter value if no key found in the values dictionary
        :return:            The configuration value
        """

        if key in values.keys():    # If key exists in the values' dictionary, return the value.
            return values.get(key, default)
        else:   # Try to search on system environment variables
            return os.environ.get(key, default)

    def _set_value(self, key, value):
        """
        Modify a configuration parameter. If parameter is commented, it will be uncommented and modify its value.
        If parameter doesn't exist, set_value will be skipped

        :param key:     Configuration key name
        :param value:   Configuration value
        :return:        Nothing
        """

        # If key is not detected, check if it is commented
        if key not in self._data.keys():
            # Try to uncomment the parameter
            self._data_uncomment_parameter(key)

        # Check if the key exits in the current values
        if key in self._data.keys():
            self._data[key] = value   # Update value
            self._data_save()   # Save data to file
            return True

        else:
            return False # Error, could not find the key

    # List of configuration parameters with setter ------------------------------------------------------------------

    # #  dsmr_raw_data_interval   -----------------------------------------------------------------------
    # @property
    # def dsmr_raw_data_interval(self):
    #     return self._get_value(self._data, "DSMR_RAW_DATA_INTERVAL", 0)



class IeconInfo:

    def __init__(self, file_path="ieconinfo.yml"):

        self.file_path = file_path

        self._parser = YAML()

        self._data_load()   # Load data from the file

        # ----- Parse configuration values -----------

        self.application = self._data.get("name", "unknown")

        self.version = self._data.get("version", "unknown")

        self.description = self._data.get("description", "unknown")

        self.author = self._data.get("author", "unknown")


    def _data_load(self):
        """
        Load the YML data from the file
        :return: boolean - Load result
        """
        try:
            with open(self.file_path) as fr:
                self._data = self._parser.load(fr)
            return True
        except:
            self._data = {}
            return False


if __name__ == "__main__":

    config = AppConfig()

    info = IeconInfo()
