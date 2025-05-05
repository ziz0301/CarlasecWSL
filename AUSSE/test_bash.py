import os
import subprocess
import time
'''
result = subprocess.run(['dbus-launch'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'DBUS_SESSION_BUS_ADDRESS' in line or 'DBUS_SESSION_BUS_PID' in line:
        key, value = line.split('=', 1)
        os.environ[key] = value
        '''
subprocess.run(['gnome-terminal', '--','bash', '--init-file', 'attacker.sh'])