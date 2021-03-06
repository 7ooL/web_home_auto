from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from hue.models import Scene as HueScene
from vivint.models import Panel
from watchers.models import CustomEvent
from carrier.models import System

#import apscheduler.job as Test


import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    SOURCE = ((-1,"------"),(0,"Vivint"),(1, "Hue"),(2,"Wemo"),(3,"Decora"))
    SOURCE_TYPE = ((-1,"------"),(0,"Bulb"),(1, "Group"),(2,"Scene"),(3,"Switch"),(4,"Plug"),(5,"Sensor"),(6,"Lock"),(7,"Motion Detector"), (8,"External Schedule"))

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
        ordering = ('name',)

class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_home = models.BooleanField(default=False)
    always_visible = models.BooleanField(default=True)
    text_address = models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)

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

class HouseSchedule(Common):
    source = models.IntegerField(choices=Common.SOURCE, default=-1)
    source_type = models.IntegerField(choices=Common.SOURCE_TYPE, default=-1)
    source_id = models.IntegerField(default=-1)

class Trigger(Common):
    DEFAULT = '-----'
    MOTION = 'Motion'
    SCHEDULE = 'External Schedule Start'
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
    PEOPLE = "People Do Something"
    CUSTOM_EVENT = "Events"

    TRIGGER_TYPES =[
        ((DEFAULT,DEFAULT)),
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
        ('People' ,(
                (PEOPLE,PEOPLE),
        )),
        ('Watcher Events' ,(
                (CUSTOM_EVENT,CUSTOM_EVENT),
        )),


    ]
    trigger = models.CharField(max_length=60,choices=TRIGGER_TYPES, default=DEFAULT)
    motion_detector = models.OneToOneField(HouseMotionDetector, on_delete=models.CASCADE, blank=True, null=True)
    sensor = models.OneToOneField(HouseSensor, on_delete=models.CASCADE, blank=True, null=True)
    lock = models.OneToOneField(HouseLock, on_delete=models.CASCADE, blank=True, null=True)
    window_start = models.TimeField(default=timezone.now)
    window_end = models.TimeField(default=timezone.now)
    external_schedule =  models.ForeignKey(HouseSchedule, on_delete=models.CASCADE, blank=True, null=True)
    external_schedule_delay = models.IntegerField(default=-1, verbose_name='Delay behind external schedule (minutes)')
    people =  models.ManyToManyField(Person, blank=True)
    people_has_left = models.BooleanField(default=False)
    people_has_arrived = models.BooleanField(default=False)
    security_panel = models.ForeignKey(Panel, on_delete=models.CASCADE, blank=True, null=True)
    security_armed_to = models.BooleanField(default=False, verbose_name="When person sets state to")
    security_changed_to = models.BooleanField(default=False, verbose_name="When state changes to")
    security_armed_state =  models.CharField(max_length=60,choices=Common.ARM_STATES, default=Common.DISARMED, verbose_name="Armed State")
    hvac_unit = models.ManyToManyField(System, blank=True)
    hvac_profile = models.CharField(max_length=60,choices=Common.HVAC_PROFILES, default=Common.HOME)
    hvac_value = models.IntegerField(default=0)
    hvac_hold = models.BooleanField(default=False)
    hvac_heat_mode = models.CharField(max_length=60,choices=Common.HVAC_HEAT_MODES, default=Common.OFF)
    event = models.OneToOneField(CustomEvent, on_delete=models.CASCADE, blank=True, null=True)

class Action(Common):
    PLAY_SCENE = 'Play Scenes'
    PLAY_RANDOM_SCENE = 'Play Random Scene'
    FLASH_SCENE = 'Flash Scene'
    TURN_ON = 'Turn On Lights'
    TURN_OFF = 'Turn Off Lights'
    BLINK_HUE = 'Blink Hue Groups'
    SEND_TEXT = 'Send a Text Message'
    HVAC_SET_ACTIVITY = 'Set HVAC Current Activity'
    SECURITY_SET_STATE = 'Set Armed State'
    PEOPLE_LEAVE = "Mark People Away"
    PEOPLE_ARRIVE = "Mark People Home"
    DISABLE_TRIGGER = "Disable Trigger"
    ENABLE_TRIGGER = "Enable Trigger"
    ACTION_TYPES =[
        ('Alter Lights',(
	        (TURN_ON,TURN_ON),
	        (TURN_OFF,TURN_OFF),
	        (PLAY_SCENE,PLAY_SCENE),
	        (PLAY_RANDOM_SCENE,PLAY_RANDOM_SCENE),
	        (BLINK_HUE,BLINK_HUE),
                (FLASH_SCENE,FLASH_SCENE),
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
        ('People Status' ,(
                (PEOPLE_LEAVE,PEOPLE_LEAVE),
                (PEOPLE_ARRIVE,PEOPLE_ARRIVE),
        )),
        ('Trigger' ,(
                (DISABLE_TRIGGER,DISABLE_TRIGGER),
                (ENABLE_TRIGGER,ENABLE_TRIGGER),
        )),

    ]

    REMOVE_HOLD = "Remove Hold"
    SET_TEMPORAY_AWAY = "Set temporary AWAY"
    HVAC_ACTIONS =[
        (REMOVE_HOLD,REMOVE_HOLD),
        (SET_TEMPORAY_AWAY,SET_TEMPORAY_AWAY),
    ]

    action = models.CharField(max_length=60,choices=ACTION_TYPES, default=TURN_ON)
    lights = models.ManyToManyField(HouseLight, blank=True)
    scenes = models.ManyToManyField(HueScene,blank=True)
    scenes_transition_time = models.IntegerField(default=4,verbose_name='Transition Time (seconds)') 
    people = models.ManyToManyField(Person,blank=True)
    text_message = models.CharField(max_length=120, default="", blank=True, null=True)
    hvac_unit = models.ManyToManyField(System, blank=True)
    hvac_actions = models.CharField(max_length=60,choices=HVAC_ACTIONS, default=REMOVE_HOLD)
    people =  models.ManyToManyField(Person, blank=True)
    triggers = models.ManyToManyField(Trigger, blank=True)
    action_grace_period = models.IntegerField(default=-1, verbose_name='Grace Period (minutes)')
    last_action_time = models.DateTimeField(default=timezone.now,blank=True, null=True)

class Nugget(Common):
    triggers =  models.ManyToManyField(Trigger, blank=False)
    actions = models.ManyToManyField(Action, blank=False)
    only_execute_if_someone_is_home = models.BooleanField(default=False)

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


