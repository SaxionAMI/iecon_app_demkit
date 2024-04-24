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

from ruamel.yaml import YAML
from pytz import timezone


demCfg = {}

# -------
#
#   SET CONFIGURATIONS IN "config.yml" FILE
#
# -------

# Loading the data from the config.yml
try:
    with open("/app/conf/config.yml") as fr:
        demCfg = YAML().load(fr)
except Exception as e:
    print("ERROR while loading usercnf data - " + str(e))

# Setting timezone object
demCfg['timezone'] = timezone(demCfg['timezonestr'])