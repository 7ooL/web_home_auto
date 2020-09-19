from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from .hue import Group, Sensor, Scene
from .wemo import Wemo
from .decora import Switch
from .vivint import Device
from .infinity import Infinity

#import apscheduler.job as Test


import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    SOURCE = ((-1,"------"),(0,"Vivint"),(1, "Hue"),(2,"Wemo"),(3,"Decora"))
    SOURCE_TYPE = ((-1,"------"),(0,"Bulb"),(1, "Group"),(2,"Scene"),(3,"Switch"),(4,"Plug"),(5,"Sensor"),(6,"Lock"),(7,"Motion Detector"))

    DISARMED = 'disarmed'
    ARMED_STAY = 'armed_stay'
    ARMED_AWAY = 'armed_away'
    ARM_STATES = [
        (DISARMED,DISARMED),
        (ARMED_STAY,ARMED_STAY),
        (ARMED_AWAY,ARMED_AWAY),
    ]

    VACATION = 'Vacation'
    MANUAL = 'Manual'
    WAKE = 'Wake'
    SLEEP = 'Sleep'
    AWAY = 'Away'
    HOME = 'Home'
    HVAC_PROFILES = [
    	(VACATION,VACATION),
    	(MANUAL,MANUAL),
    	(WAKE,WAKE),
    	(SLEEP,SLEEP),
    	(AWAY,AWAY),
    	(HOME,HOME),
    ]

    # need to be set for your system config: hpheat, hpelectheat, gasheat, cool, off
    OFF = 'off'
    COOL = 'cool'
    HEAT = 'gasheat'
    DEHUMID = 'dehumidify'
    HVAC_HEAT_MODES = [
    	(OFF,OFF),
    	(COOL,COOL),
    	(HEAT,HEAT),
        (DEHUMID,DEHUMID),
    ]

    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    name = models.CharField(max_length=60)
    enabled = models.BooleanField(default=True)
    def __str__(self):
        return '{}'.format(self.name)
    class Meta:
        abstract = True

class Job(models.Model):
    COMMAND_TYPES = (
        ('','-------'),
        (0,'Dropbox AutoStart'),
        (1,'Wemo Pull and DB Update'),
        (2,'Decora Pull and DB Update'),
        (3,'Vivint Pull and DB Update'),
        (4,'Hue Groups Pull and DB Update'),
        (5,'Hue Lights Pull and DB Update'),
        (6,'Hue Scenes Pull and DB Update'),
        (7,'Hue Sensors Pull and DB Update'),
        (8,'Hue Schedules Pull and DB Update'),
        (9,'Find Motion Detectors in Devices'),
        (10,'Find House Lights in Devices'),
        (11,'Evaluate Time Based Triggers'),
        (12,'Find House Locks in Devices'),
        (13,'Find House Sensors in Devices'),
        (14,'Infinity System Pull DB Update'),
    )
    command = models.IntegerField(choices=COMMAND_TYPES, default='')
    interval = models.IntegerField(default=600,validators=[MinValueValidator(0),MaxValueValidator(3600)] )
    enabled = models.BooleanField(default=False)

#    def save(self, *args, **kwargs):
#        test = self
#        super(Job, self).save(*args, **kwargs)
#        jobs.createJobs(test)
#        logger.debug("Running create job for "+self.COMMAND_TYPES[self.command+1][1])
#        if self.enabled:
#            if self.command == 0:
#                try:
#                    jobs.scheduler.add_job(jobs.dropbox_job,'interval', seconds=self.interval, id=self.COMMAND_TYPES[self.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
#                except OperationalError as error:
#                    logger.error("job not added")
#            else:
#                logger.warning("No job has been created for command: "+self.COMMAND_TYPES[self.command+1][1])
#        else:
#            logger.debug(self.COMMAND_TYPES[self.command+1][1]+" was not enabled so it was not created")
#        with transaction.atomic():





class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_home = models.BooleanField(default=False)
    always_visible = models.BooleanField(default=True)
    text_address = models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)

class Zone(Common):
    huegroups = models.ManyToManyField(Group, blank=True)
    sensors = models.ManyToManyField(Sensor, blank=True)
    wemos = models.ManyToManyField(Wemo, blank=True)
    decora = models.ManyToManyField(Switch, blank=True)
    vivint = models.ManyToManyField(Device, blank=True)
    def __str__(self):
        return '{}'.format(self.name)

class HouseMotionDetector(Common):
    source = models.IntegerField(choices=Common.SOURCE, default=-1)
    source_type = models.IntegerField(choices=Common.SOURCE_TYPE, default=-1)
    source_id = models.IntegerField(default=-1)

class HouseLight(Common):
    source = models.IntegerField(choices=Common.SOURCE, default=-1)
    source_type = models.IntegerField(choices=Common.SOURCE_TYPE, default=-1)
    source_id = models.IntegerField(default=-1)

class HouseLock(Common):
    source = models.IntegerField(choices=Common.SOURCE, default=-1)
    source_type = models.IntegerField(choices=Common.SOURCE_TYPE, default=-1)
    source_id = models.IntegerField(default=-1)

class HouseSensor(Common):
    source = models.IntegerField(choices=Common.SOURCE, default=-1)
    source_type = models.IntegerField(choices=Common.SOURCE_TYPE, default=-1)
    source_id = models.IntegerField(default=-1)

class Trigger(Common):
    MOTION = 'Motion'
    SCHEDULE = 'Specific Time'
    WINDOW ='Time Window'
    SENSOR_OPENED = 'Sensor Opened'
    SENSOR_CLOSED = 'Sensor Closed'
    LOCK_UNLOCKED = 'Lock is Unlocked'
    LOCK_LOCKED = 'Lock is Locked'
    HVAC_ACTIVITY = 'Currenty Activity'
    HVAC_FAN = 'Fan'
    HVAC_HITS_TEMP = 'Hits Temperature'
    HVAC_HOLD = "Hold Setting"
    HVAC_HEATMODE = 'Heat Mode'
    HVAC_FILTRLVL = 'Filter Level'
    HVAC_HUMLVL = 'Humidity Level'
    SECURITY_ARMED_STATE = 'Armed State'

    TRIGGER_TYPES =[
        ('Time' ,(
	        (SCHEDULE, SCHEDULE),
	        (WINDOW, WINDOW),
        )),
        ('Sensors',(
                (MOTION, MOTION),
	        (SENSOR_OPENED, SENSOR_OPENED),
	        (SENSOR_CLOSED, SENSOR_CLOSED),
	        (LOCK_UNLOCKED, LOCK_UNLOCKED),
	        (LOCK_LOCKED, LOCK_LOCKED),
        )),
        ('HVAC' ,(
                (HVAC_ACTIVITY,HVAC_ACTIVITY),
                (HVAC_FAN,HVAC_FAN),
                (HVAC_HITS_TEMP,HVAC_HITS_TEMP),
                (HVAC_HOLD,HVAC_HOLD),
                (HVAC_HEATMODE,HVAC_HEATMODE),
                (HVAC_FILTRLVL,HVAC_FILTRLVL),
                (HVAC_HUMLVL,HVAC_HUMLVL),
        )),
        ('Security' ,(
                (SECURITY_ARMED_STATE,SECURITY_ARMED_STATE),
        )),

    ]
    trigger = models.CharField(max_length=60,choices=TRIGGER_TYPES, default=MOTION)
    motion_detector = models.OneToOneField(HouseMotionDetector, on_delete=models.CASCADE, blank=True, null=True)
    sensor = models.OneToOneField(HouseSensor, on_delete=models.CASCADE, blank=True, null=True)
    lock = models.OneToOneField(HouseLock, on_delete=models.CASCADE, blank=True, null=True)
    window_start = models.TimeField(default=timezone.now)
    window_end = models.TimeField(default=timezone.now)
    schedule_start = models.TimeField(default=timezone.now)
    people =  models.ManyToManyField(Person, blank=True)
    armed_state =  models.CharField(max_length=60,choices=Common.ARM_STATES, default=Common.DISARMED)
    hvac_unit = models.ManyToManyField(Infinity, blank=True)
    hvac_profile = models.CharField(max_length=60,choices=Common.HVAC_PROFILES, default=Common.HOME)
    hvac_value = models.IntegerField(default=0)
    hvac_hold = models.BooleanField(default=False)
    hvac_heat_mode = models.CharField(max_length=60,choices=Common.HVAC_HEAT_MODES, default=Common.OFF)

class Action(Common):
    TURN_ON = 'Turn On Lights'
    TURN_OFF = 'Turn Off Lights'
    PLAY_SCENE = 'Play a Scene'
    BLINK_HUE = 'Blink a Hue Group'
    SEND_TEXT = 'Send a Text Message'
    HVAC_SET_ACTIVITY = 'Set HVAC Current Activity'
    SECURITY_SET_STATE = 'Set Armed State'
    ACTION_TYPES =[
        ('Alter Lights',(
	        (TURN_ON,TURN_ON),
	        (TURN_OFF,TURN_OFF),
	        (PLAY_SCENE,PLAY_SCENE),
	        (BLINK_HUE,BLINK_HUE),
        )),
        ('Notifications',(
	        (SEND_TEXT,SEND_TEXT),
        )),
        ('HVAC' ,(
                (HVAC_SET_ACTIVITY,HVAC_SET_ACTIVITY),
        )),
        ('Security' ,(
                (SECURITY_SET_STATE,SECURITY_SET_STATE),
        )),
    ]

    action = models.CharField(max_length=60,choices=ACTION_TYPES, default=TURN_ON)
    lights = models.ManyToManyField(HouseLight, blank=True)
    scene = models.OneToOneField(Scene,on_delete=models.CASCADE, blank=True, null=True)
    people = models.ManyToManyField(Person,blank=True)
    text_message = models.CharField(max_length=120, default="", blank=True, null=True)
    action_grace_period = models.IntegerField(default=-1)
    last_action_time = models.DateTimeField(default=timezone.now,blank=True, null=True)


class Nugget(Common):
    triggers =  models.ManyToManyField(Trigger, blank=False)
    actions = models.ManyToManyField(Action, blank=False)



#class Action(Common):
#    WEMO_ACTIONS = ((1,'Turn ON'),(0,'Turn Off'), (-1, 'None'))
#    DECORA_ACTIONS = ((1,'Turn ON'),(0,'Turn Off'), (-1, 'None'))
#    HUE_ACTIONS = ((1,'Turn ON'),(0,'Turn Off'),(3,'Play Scene'),(-1,'None'))
#
#    VIVINT_ACTIONS = ((3,'Arm Stay'),(2, 'Arm Away'), (0,'Disarmed'), (5,'Lock Door'),(6, 'Unlock Door'), (7,'Opem Garage'), (8,' Close Garage'),(-1,'None'))
#    hue_action = models.IntegerField(choices=HUE_ACTIONS, default=-1)
#    wemo_action = models.IntegerField(choices=WEMO_ACTIONS, default=-1)
#    decora_action = models.IntegerField(choices=DECORA_ACTIONS, default=-1)
#    vivint_action = models.IntegerField(choices=VIVINT_ACTIONS, default=-1)



#    schedule = Test()
#    zone = models.ManyToManyField(Zone)
#    actions = models.ManyToManyField(Action)



class Account(Common):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=32)
    sessionKey = models.TextField(null=True, blank=True)
    def __str__(self):
        if self.enabled:
            enabled = "ENABLED"
        else:
            enabled = "DISABLED"
        return '{} - {}'.format(self.name, enabled)

#    def save(self, *args, **kwargs):
#        super(Account, self).save(*args, **kwargs)
#        if self.name == 'Vivint':
#            from homeauto import vivint
#            if self.enabled:
#                vivint.start()
#            else:
#                vivint.end()

