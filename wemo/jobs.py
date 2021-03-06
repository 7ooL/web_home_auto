from wemo.models import Device, Account
from jobs.jobs import build_jobs
from django.core.exceptions import ObjectDoesNotExist

import subprocess, logging

logger = logging.getLogger(__name__)

def start():
    JOBS = (
        ('Wemo', 'Get Wemo Status and Update Database', False, 20, sync_wemo),
    )
    build_jobs(JOBS)


def sync_wemo():
    from distutils.spawn import find_executable
    try:
        wemoAcct = Account.objects.get(pk=1)
    except ObjectDoesNotExist as e:
        logger.error(e)
        logger.error('No Wemo User is defined')
    except:
        logger.error("Error:"+ str(traceback.format_exc()))
    else:
        if find_executable('wemo') is not None:
            logger.debug("'wemo' command exists")
            logger.debug('Syncing Wemo Data')
            cmd = '/usr/local/bin/wemo status'
            proc = subprocess.Popen([cmd], stdout=(subprocess.PIPE), shell=True)
            out, err = proc.communicate()
            if out:
                logger.debug(out)
                devices = out.rstrip(b'\n').decode()
                devices = devices.replace(':', '')
                devices = devices.split('\n')
                logger.debug("devices")
                logger.debug(devices)
                x = 0
                for device in devices:
                    logger.debug("device")
                    logger.debug(device)
                    attr = []
                    attr.append(device.split(' ',1)[0].strip()) # type
                    logger.debug("type: "+str(attr[0]))
                    attr.append(device.split(' ',1)[1].split('\t')[0].strip()) # name
                    logger.debug("name: "+str(attr[1]))
                    attr.append(device.split('\t')[1].strip()) # status
                    logger.debug("status: "+str(attr[2]))
                    devices[x] = attr
                    x = x + 1
                for device in devices:
                    logger.debug("device: "+str(device))
                    if not Device.objects.filter(name__iexact=(device[1])).exists():
                        logger.debug('Name: ' + str(device[1]) + ' does not exist')
                        logger.debug(device)
                        logger.info('Creating wemo:' + device[1])
                        data = {}
                        data['status'] = device[2]
                        data['type'] = device[0]
                        data['name'] = device[1]
                        w = (Device.objects.create)(**data)
                        w.save()
                        log_addition(wemoAcct, w)
                    else:
                        xWemo = Device.objects.get(name__iexact=(device[1]))
                        if xWemo.name != device[1]:
                            logger.info('Updating name for ' + str(device[1]) + ': ' + str(device[2]))
                            xWemo.name = device[1]
                            xWemo.save()
                        if xWemo.type != device[0]:
                            logger.info('Updating type for ' + str(device[1]) + ': ' + str(device[2]))
                            xWemo.type = device[0]
                            xWemo.save()
                        if xWemo.status != int(device[2]):
                            logger.info('Updating status for ' + str(device[1]) + ': ' + str(device[2]))
                            xWemo.status = device[2]
                            xWemo.save()
            else:
                logger.warning("'wemo status' command returned empty string")
        else:
            logger.error("Cannot sync Wemo data because no Wemo (ouimeaux) executable exist")


from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

def log_addition(acct, object):
    """
    Log that an object has been successfully added.
    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, ADDITION
    LogEntry.objects.log_action(
        user_id=acct.user.id,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        object_repr=force_text(object),
        action_flag=ADDITION
    )

