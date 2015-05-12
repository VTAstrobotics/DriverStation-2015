# Config files and instructions for Raspberry PI driver station

Instructions for setting up the pi as a driver station:
1. Make sure xboxdrv is installed
2. Copy the lines from `rc.local` file here into `/etc/rc.local` on the pi (before the `exit 0` line)
3. Copy the file `interfaces` to `/etc/network/`, overwriting the file that already exists there
4. Clone the git repo git@github.com:VTAstrobotics/DriverStation-2015.git into /home/pi/
5. Driver station should run automatically at reboot
