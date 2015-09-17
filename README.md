![alt text](https://github.com/ellak-monades-aristeias/nagios-autoIDM/blob/master/misc/logo.png "Auto IDM Logo")

### Nagios extension for Automatic scanning, Identification and Monitoring of networked devices

This project aims to create a user-friendly web GUI for nagios, enabling the network administrator to:

* Scan an entire subnet
* Automatically find new network devices that should be monitored
* Detect any service running on each new device
* Identify the type of the device, based on the services running

For each detected device, AutoIDM automatically reconfigures Nagios in order to monitor this device, performing the necessary checks according to the type of the device.

Currently supported devices are:

1. Linux Hosts
2. Windows Hosts
3. VMWare Hypervisors
4. Switches
5. Routers
6. NAS devices
7. Asterisk servers
8. IP phones

You can find more information, as well as step-by-step guide for the installation of autoIDM extension in our [Wiki]

Screenshot:
--------------
![alt text](https://github.com/ellak-monades-aristeias/nagios-autoIDM/blob/master/misc/Screenshot.png "Screenshot")
   [Wiki]: <https://github.com/ellak-monades-aristeias/nagios-autoIDM/wiki>
