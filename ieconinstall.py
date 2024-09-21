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
    print("Loading config")
    with open(os.path.join(folder_installation, "conf", "config.yml"), "r") as fr:
        config = YAML().load(fr)

    # print(global_env)

    # Update configuration values based on custom IECON parameters
    # config['db']['influx']['dbname'] = global_env.get("IECON_GROUP_NAME", "IECON")
    config['db']['influx']['address'] = global_env.get("IECON_INFLUXDB2_HOST", "localhost")
    config['db']['influx']['port'] = global_env.get("IECON_INFLUXDB2_PORT", 8086)
    config['db']['influx']['username'] = global_env.get("IECON_INFLUXDB2_USER", "")
    config['db']['influx']['password'] = global_env.get("IECON_INFLUXDB2_PASS", "")
    config['db']['influx']['token'] = global_env.get("IECON_INFLUXDB2_ADMIN_TOKEN", "")
    config['db']['influx']['org'] = global_env.get("IECON_INFLUXDB2_ORG", "iecon")

    # MQTT spb configuration
    config['mqtt_spb']['address'] = global_env.get("IECON_MQTT_HOST", "localhost")
    config['mqtt_spb']['port'] = global_env.get("IECON_MQTT_PORT", 1883)
    config['mqtt_spb']['username'] = global_env.get("IECON_MQTT_USER", "")
    config['mqtt_spb']['password'] = global_env.get("IECON_MQTT_PASS", "")

    # Application path
    config["app_path"] = folder_installation

    # print(config)

    # Save configuration file
    print("Saving config")
    with open(os.path.join(folder_installation, "conf", "config.yml"), "w") as fw:
        YAML().dump(config, fw)

    # Generate Environment file-----------------------------------------------------------------------------------
    print("Generating .env")
    with open(os.path.join(folder_installation, ".env"), "w") as fw:
        fw.write('FOLDER_IECON_APP_DEMKIT="%s"\n' % folder_installation)

if __name__ == "__main__":

    build()

