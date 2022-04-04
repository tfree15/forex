
import os
import subprocess
import configparser
import stats_calc_publish.tradepoint_birt_reports.scripts as _

#i Read in config properties file for script arguments
config = configparser.ConfigParser()
config.read('/usr/app/fxda/birt_report/cfg/quant_stats.properties')

# Retrive host enviornment
env = os.uname()[1].split('.'[0])[1]
s = config[env]['script_name']

# Source Python script name from stats_calc_publish.tradepoint_birt_reports.scripts"
pkg_path = _.__path__
script =  f'{pkg_path[0]}/{s}'
birt_report = f"python {script}"

# Call stats_calc_publish.tradepoint_birt_reports.scripts script
try:
        subprocess.call([birt_report], shell=True)
except Exception as error:
        print(f"ERROR: Could not call {script}")
