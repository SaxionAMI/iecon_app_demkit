"""
    -- IECON Module installation script --

"""
from ruamel.yaml import YAML
import os


def build(folder_installation="./", global_env={}):
    """
        Module custom installation steps
    """

    # Update DEMKIT conf/config.yml files with IECON specific parameters ------------------------------------------------

    # CONFIG - Update Configuration file with MQTT information
    config_file_path = os.path.join(folder_installation, "config.yml")
    print("Loading config from: " + config_file_path )
    with open(config_file_path, "r") as fr:
        config = YAML().load(fr)

    # print("gloval_env=", global_env)  # Uncomment to see what it is passed

    # ----------------------------------------------------------------------------
    #   IECON Parameters
    # ----------------------------------------------------------------------------

    if not config.get('IECON_SPB_DOMAIN_ID', None):
        config['IECON_SPB_DOMAIN_ID'] = global_env.get("IECON_SPB_GROUP_NAME", "IECON")

    # MQTT broker
    config['IECON_MQTT_HOST'] = global_env.get("IECON_MQTT_HOST", "localhost")
    config['IECON_MQTT_PORT'] = global_env.get("IECON_MQTT_PORT", 1883)
    config['IECON_MQTT_USER'] = global_env.get("IECON_MQTT_USER", "")
    config['IECON_MQTT_PASS'] = global_env.get("IECON_MQTT_PASS", "")

    # InfluxDB 2x
    config['IECON_INFLUXDB2_HOST'] = global_env.get("IECON_INFLUXDB2_HOST", "localhost")
    config['IECON_INFLUXDB2_PORT'] = global_env.get("IECON_INFLUXDB2_PORT", 8086)
    config['IECON_INFLUXDB2_USER'] = global_env.get("IECON_INFLUXDB2_USER", "")
    config['IECON_INFLUXDB2_PASS'] = global_env.get("IECON_INFLUXDB2_PASS", "")
    config['IECON_INFLUXDB2_ADMIN_TOKEN'] = global_env.get("IECON_INFLUXDB2_ADMIN_TOKEN", "")
    config['IECON_INFLUXDB2_ORG'] = global_env.get("IECON_INFLUXDB2_ORG", "iecon")

    # ----------------------------------------------------------------------------
    #   DEMKIT Legacy Parameters
    # ----------------------------------------------------------------------------

    # Update configuration values based on custom IECON parameters
    if not config['db']['influx']['dbname']:
        config['db']['influx']['dbname'] = global_env.get("IECON_SPB_GROUP_NAME", "IECON") + "-DEMKIT"

    config['db']['influx']['address'] = global_env.get("IECON_INFLUXDB2_HOST", "localhost")
    config['db']['influx']['port'] = global_env.get("IECON_INFLUXDB2_PORT", 8086)
    config['db']['influx']['username'] = global_env.get("IECON_INFLUXDB2_USER", "")
    config['db']['influx']['password'] = global_env.get("IECON_INFLUXDB2_PASS", "")
    config['db']['influx']['token'] = global_env.get("IECON_INFLUXDB2_ADMIN_TOKEN", "")
    config['db']['influx']['org'] = global_env.get("IECON_INFLUXDB2_ORG", "iecon")

    # print(config)

    # Save configuration file
    print("Saving config :" + config_file_path)
    with open(config_file_path, "w") as fw:
        YAML().dump(config, fw)

    # Generate Environment file-----------------------------------------------------------------------------------
    print("Generating .env")
    with open(os.path.join(folder_installation, ".env"), "w") as fw:
        fw.write('FOLDER_IECON_APP_DEMKIT="%s"\n' % folder_installation)

if __name__ == "__main__":

    build()

