from django.db import models
from django.contrib.auth.models import User

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    name = models.CharField(max_length=30)
    enabled = models.BooleanField(default=False, verbose_name='Discoverable By HomeAuto')
    class Meta:
        ordering = ['name']
    def __str__(self):
        if self.enabled:
          enabled = "ENABLED"
        else:
          enabled = "DISABLED"
        return '{} - {}'.format(self.name, enabled)
    class Meta:
        abstract = True
#        app_label = 'Devices'

class Device(Common):
    type = models.CharField(max_length=30)
    status = models.BooleanField(default=False, verbose_name='On')

class Account(models.Model):
    class Meta:
        verbose_name_plural = 'Application Account'
    user = models.OneToOneField(User, related_name='wemo_account_created', on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        self.pk = 1
        super(Account, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj




