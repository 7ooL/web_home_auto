## Background on the HomAuto project.
My home automation program has been a work of several years and is used to automate everything that can be in my house. 

It originally started out as a python-based set of scripts that would read and write from text-based content with a structure and syntax comprising of key-value pairs. That project is here.  https://github.com/7ooL/home_auto_scripts
While these scripts work just fine, they do not take kindly to updates. Updates in the form of new smart home devices and changes to any configurations already set.  There was no real interface and all updates required new code changes. There were a few different front-end dashboard style interfaces along the way, but nothing that allowed for to much interactions. 

# HomeAuto
This is a Django based application that makes used of the admin site to administer all aspects of this home automation program.  
Automation is achieved in two main ways.

1)	Scheduled Jobs 
2)	Nugget firing.

## Jobs
First, jobs can be scheduled to do things on a regular basis. There are a number of pre-defined jobs, for example, many that update devices status and look for new devices. Each job can be fine tuned to run at its own frequency depending on what makes sense. Syncing light states from Hue devices is more important than checking if new groups have been defined. 

![Image of Jobs](https://github.com/7ooL/HomeAuto/blob/master/images/add_job.png)

## Nuggets
Nuggets are made up of Triggers and Actions. When all the Triggers in a Nugget are TRUE then its Actions will be executed. It's this framework that allows for the expansion of automation through a web interface. 

![Image of Nugget](https://github.com/7ooL/HomeAuto/blob/master/images/nugget.png)

### Triggers
Triggers become TRUE when certain events occur. For example when it’s a specific time, when a door is opened, or when motion is detected. 
Once a Trigger is defined it can be used in multiple Nuggets, or even combined with other Triggers in a Nugget. 

![Image of Triggers](https://github.com/7ooL/HomeAuto/blob/master/images/triggers.png)

### Actions
Actions are what happens when all the Triggers in a Nugget become TRUE.

![Image of Actions](https://github.com/7ooL/HomeAuto/blob/master/images/actions.png)

## House Devices
One of the things that HomeAuto does is normalize devices form multiple manufactures into House objects. Current House Objects consist of:

* House Lights
* House Locks
* House Sensors
* House Motion Detectors

This allows for example Hue Light Bulbs, Decora Switches, and WeMo Plugs to be combined and controlled as House Lights. 
If I ever get a new device from a different manufacture, it would be just a matter of integrating into the House Models. This happens much less frequent then add a new device from an existing manufacturer.  

HomeAuto currently supports devices from the following:
### Phillips Hue
* Bridges (syncing devices)
* Lights (triggers and actions)
* Sensors (triggers)
* Groups (actions)
* Schedules (triggers)
* Scenes (actions)
### Leviton Decora Wifi
* api account (syncing devices)
* Switches (triggers and actions)
### Wemo
* Wifi Smart Plug (triggers and actions)
### Vivint Security System
* Sensors (triggers)
* Locks (triggers and actions)
* Panel (syncing devices)
* Alarm (triggers)
* Camera (triggers)
### Carrier Infinity
* Systems (syncing devices)
* Profiles (actions)
* Activities (actions)
* Status (triggers and actions)
