#!/usr/bin/python3

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


import argparse
import importlib
import os
import sys
from conf.usrconf import load_demkit_config

sys.stderr.write("_________________________________________________________________________________________________\n")
sys.stderr.write('      --- IECON Application DEMKit ---\n')
sys.stderr.write('       Based on DEMKIT version 2023.3\n\n')
sys.stderr.write('Copyright 2023 University of Twente, Enschede, the Netherlands\n\n')
sys.stderr.write('Licensed under the Apache License, Version 2.0 (the "License")\n')
sys.stderr.write("_________________________________________________________________________________________________\n")
sys.stderr.flush()

if len(sys.argv) > 1:

    # Move to the application folder
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    app_path = os.getcwd()  # Save the current application path

    sys.stderr.write(f"Current working directory: {os.getcwd()} " + "\n")

    # Add config path to the system
    sys.path.insert(0, os.path.join(app_path, 'conf/'))  # Add to system path

    # Load config file
    from conf.usrconf import demCfg

    try:
        if demCfg['ver'] < 4:
            sys.stderr.write(
                "[ERROR] Incorrect configuration version found. Make sure to have a proper conf/usrconf.py file!"
                " Please refer to the provided exanple.\n")
            sys.stderr.flush()
            exit()

        if demCfg['ver'] < 4.1:
            sys.stderr.write(
                "\n[WARNING] Old configuration version detected."
                " Please refer to the usrconf.py.misc example file to see the changes.\n"
            )
            sys.stderr.write(
                "[WARNING] DEMKit will use the default values for missing configuration entries"
                " but manual configuration is advised.\n"
            )
            sys.stderr.write("[WARNING] Current expected config version is: 4.1.\n")
            sys.stderr.write("[WARNING] Changelog:  \n")
            sys.stderr.write("[WARNING] Version 4.1 adds: demCfg['var'] entries and demCfg['timezone'] entry. \n\n")
            sys.stderr.flush()

            # Variable output for logs ans backups (stored within the workspace folder of a model by default)
            demCfg['var'] = {}
            demCfg['var']['backup'] = os.path.join(app_path, "var/backup/")
            demCfg['var']['databasebackup'] = os.path.join(app_path, "var/backup/database/")
            demCfg['var']['log'] = os.path.join(app_path, "var/log/")

            # Timezone information
            from pytz import timezone

            demCfg['timezonestr'] = 'Europe/Amsterdam'
            demCfg['timezone'] = timezone(demCfg['timezonestr'])

        # Add trailing slash
        if demCfg['env']['path'][-1] != '\\' and demCfg['env']['path'][-1] != '/':
            demCfg['env']['path'] += '/'
        if demCfg['workspace']['path'][-1] != '\\' and demCfg['workspace']['path'][-1] != '/':
            demCfg['workspace']['path'] += '/'

    except:
        sys.stderr.write(
            "Errors occurred when loading the configuration file. Make sure to have a proper conf/usrconf.py file!"
            " Please refer to the provided exanple.\n"
        )
        sys.stderr.flush()
        exit()

    sys.stderr.write('pyDEM directory: ' + demCfg['env']['path'] + '\n')
    sys.stderr.write('User model directory: ' + demCfg['workspace']['path'] + '\n')
    sys.stderr.flush()

    # Load the DEM platform
    sys.path.insert(0, os.path.join(app_path, demCfg['env']['path']))

    modelPath = demCfg['workspace']['path']
    try:
        modelName = demCfg['model']['name']
    except:
        modelName = ""

    # Get arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder')
    parser.add_argument('-m', '--model')
    parser.add_argument('-s', '--socket')
    parser.add_argument('-u', '--smarthouseusb')

    # Parse arguments
    args = parser.parse_args()
    if args.folder:
        if (args.folder[:1] == "/") or (args.folder[:2] == "~/"):
            modelPath = args.folder
        else:
            modelPath += args.folder
    if args.model:
        modelName = args.model
    if args.socket:
        demCfg['network']['sockPath'] = args.socket
    if args.smarthouseusb:
        demCfg['smarthouse']['usb'] = args.smarthouseusb

    sys.stderr.write('Loading model: ' + modelName + ' from ' + modelPath + '\n')
    sys.stderr.flush()

    # import the model path
    sys.path.insert(0, os.path.join(app_path, modelPath))

    # change the working directory to the model directory
    os.chdir(modelPath)

    # Load the desired model
    importlib.import_module(modelName)

else:
    sys.stderr.write("Usage:" + '\n')
    sys.stderr.write('demkit.py -f <folder> -m <model> [-d <database>] [-c] [-s <socket>] [-u <smarthouseusb>]' + '\n')
    sys.stderr.flush()
