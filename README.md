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

Specifically, for:
* **Users:**  
  Users kai find detailed usage guidelines in [this](https://github.com/ellak-monades-aristeias/nagios-autoIDM/wiki/Usage-Guide#autoidm-usage-guidelines) Wiki link

* **Administrators/Developers/Contributors:**
  To further configure, or extend the functionality of AutoIDM regarding the supported network devices and service-tests, administrators and Developers/Contributors can start with [this](https://github.com/ellak-monades-aristeias/nagios-autoIDM/wiki/Usage-Guide#autoidm-extension-configuration-options) link.  

  New feature requests or issues with the existing implementation can be submitted as _Issues_ in our github project page
  

Screenshot:
--------------
![alt text](https://github.com/ellak-monades-aristeias/nagios-autoIDM/blob/master/misc/Screenshot.png "Screenshot")
   [Wiki]: <https://github.com/ellak-monades-aristeias/nagios-autoIDM/wiki>



Παραδοτέα Έργου:
--------------

| Ανάπτυξη Περιβάλλοντος Εργασίας – 1ο Παραδοτέο  | https://github.com/ellak-monades-aristeias/nagios-autoIDM/wiki/Setting-up-the-environment |
|---|---|
| **Τεκμηρίωση – 2ο Παραδοτέο**  |**Installation Guide:** https://github.com/ellak-monades-aristeias/nagios-autoIDM/wiki/Installation-Guide **Usage Guide:** https://github.com/ellak-monades-aristeias/nagios-autoIDM/wiki/Usage-Guide
  |
  
  
----------------------------------

###ACKNOWLEDGEMENT
This project is supported by the Greek Free/Open Source Software Society (GFOSS)

----------------------------------
Copyright 2015 KOSTAS GIOTIS

Licensed under the EUPL, Version 1.1
