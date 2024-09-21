# Copyright 2023 University of Twente

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This file is a template to setup DEMKit
# It is important to modify appropriate lines for your system
# Each config item should only appear once, comment the others
# Rename this file to userconf.py

import os
from ruamel.yaml import YAML
from pytz import timezone

# -------
#
#   SET CONFIGURATIONS IN "config.yml" FILE
#
# -------
def load_demkit_config(config_path=None):

    temp = {}

    # If emtpy config path, load the default config file.
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.yml")

    # Loading the data from the config.yml
    try:
        with open(config_path) as fr:
            temp = YAML().load(fr)

        # Setting timezone object
        temp['timezone'] = timezone(temp['timezonestr'])

    except Exception as e:
        print("ERROR while loading usercnf data - " + str(e))
        pass

    return temp

demCfg = load_demkit_config()  # Load the default config file

