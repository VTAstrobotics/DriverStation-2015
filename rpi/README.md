# Config files and instructions for Raspberry PI driver station

Instructions for setting up the pi as a driver station:
1. Fix SSH issues by adding `UseDNS no` to end of `/etc/ssh/sshd_config` file
2. Make sure xboxdrv is installed
3. Copy the lines from `rc.local` file here into `/etc/rc.local` on the pi (before the `exit 0` line)
4. Copy the file `interfaces` to `/etc/network/`, overwriting the file that already exists there
5. Clone the git repo git@github.com:VTAstrobotics/DriverStation-2015.git into /home/pi/
6. Driver station should run automatically at reboot

