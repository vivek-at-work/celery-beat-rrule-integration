from django.db import models
from .rruleschedule import rrule
from django_celery_beat.models import PeriodicTask,PeriodicTasks
from django.db.models import signals
from datetime import datetime
# Create your models here.

class RRuleSchedule(models.Model):
    frequency =  models.IntegerField(default=1)#interval
    starts_on = models.DateTimeField(auto_now_add=True) #dtstart
    inter = models.IntegerField(default=1)#interval
    count = models.IntegerField(null=True)#count
    ends_on = models.DateTimeField(null=True) #until
    bysetpos  = models.IntegerField(null=True)#bysetpos
    bymonth = models.IntegerField(null=True)#bymonth
    bymonthday = models.IntegerField(null=True)#bymonthday
    byyearday = models.IntegerField(null=True)#byyearday
    byeaster = models.IntegerField(null=True)#byeaster
    byweekno = models.IntegerField(null=True)#byweekno
    byweekday = models.IntegerField(null=True)#byweekday
    byhour = models.IntegerField(null=True)#byhour
    byminute = models.IntegerField(null=True)#byminute
    bysecond = models.IntegerField(null=True)#bysecond
    
    class Meta:
        """Table information."""

        verbose_name = ('RRuleSchedule')
        verbose_name_plural = ('RRuleSchedules')
        ordering = ['frequency', 'starts_on',
                    'ends_on']

    def __str__(self):
        return str(self.schedule)
        
    @property
    def schedule(self):
        return rrule(
              self.frequency, self.starts_on,
              self.inter, None, self.count, self.ends_on, self.bysetpos,
              self.bymonth, self.bymonthday, self.byyearday, self.byeaster,
              self.byweekno, self.byweekday,
              self.byhour, self.byminute, self.bysecond,
        )
        # rrule
    @property
    def next_run_at(self):
        return self.schedule.rrule.after(datetime.now())

    @property
    def get_all_runs(self):
        return [x for x in self.schedule.rrule]
        

    @classmethod
    def from_schedule(cls, schedule):

        spec =  {
            'frequency': schedule.freq,
            'starts_on':schedule.dtstart,
            'inter':schedule.interval,
            'count':schedule.count,
            'ends_on':schedule.until,
            'bysetpos' :schedule.bysetpos,
            'bymonth':schedule.bymonth,
            'bymonthday':schedule.bymonthday,
            'byyearday' :schedule.byyearday,
            'byeaster':schedule.byeaster,
            'byweekno':schedule.byweekno,
            'byweekday':schedule.byweekday,
            'byhour':schedule.byhour,
            'byminute':schedule.byminute,
            'bysecond':schedule.bysecond
        }
        try:
            return cls.objects.get(**spec)
        except cls.DoesNotExist:
            return cls(**spec)
        except MultipleObjectsReturned:
            cls.objects.filter(**spec).delete()
            return cls(**spec)



class CustomePeriodicTask(PeriodicTask):
    """Model representing a periodic task."""

    
    # You can only set ONE of the following schedule FK's
    # TODO: Redo this as a GenericForeignKey
    rrule = models.ForeignKey(
        RRuleSchedule, on_delete=models.CASCADE,
        null=True, blank=True, verbose_name=('RRule  Schedule'),
        help_text=('RRule Schedule to run the task on.  '
                    'Set only one schedule type, leave the others null.'),
    )
   

    class Meta:
        """Table information."""

        verbose_name = ('periodic task')
        verbose_name_plural = ('periodic tasks')

    def validate_unique(self, *args, **kwargs):
        schedule_types = ['interval', 'crontab', 'solar', 'clocked','rrule']
        selected_schedule_types = [s for s in schedule_types
                                   if getattr(self, s)]

        if len(selected_schedule_types) == 0:
            raise ValidationError({
                'interval': [
                    'One of clocked, interval, crontab, rrule, or solar must be set.'
                ]
            })

        err_msg = 'Only one of clocked, interval, crontab, rrule '\
            'or solar must be set'
        if len(selected_schedule_types) > 1:
            error_info = {}
            for selected_schedule_type in selected_schedule_types:
                error_info[selected_schedule_type] = [err_msg]
            raise ValidationError(error_info)

        # clocked must be one off task
        if self.clocked and not self.one_off:
            err_msg = 'clocked must be one off, one_off must set True'
            raise ValidationError(err_msg)

    def save(self, *args, **kwargs):
        self.exchange = self.exchange or None
        self.routing_key = self.routing_key or None
        self.queue = self.queue or None
        self.headers = self.headers or None
        if not self.enabled:
            self.last_run_at = None
        super(CustomePeriodicTask, self).save(*args, **kwargs)

    def __str__(self):
        fmt = '{0.name}: {{no schedule}}'
        if self.rrule:
            fmt = '{0.name}: {0.rrule}'
        if self.interval:
            fmt = '{0.name}: {0.interval}'
        if self.crontab:
            fmt = '{0.name}: {0.crontab}'
        if self.solar:
            fmt = '{0.name}: {0.solar}'
        if self.clocked:
            fmt = '{0.name}: {0.clocked}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.interval:
            return self.interval.schedule
        if self.crontab:
            return self.crontab.schedule
        if self.solar:
            return self.solar.schedule
        if self.clocked:
            return self.clocked.schedule
        if self.rrule:
            return self.rrule.schedule




signals.pre_delete.connect(PeriodicTasks.changed, sender=CustomePeriodicTask)
signals.pre_save.connect(PeriodicTasks.changed, sender=CustomePeriodicTask)
signals.post_delete.connect(
    PeriodicTasks.update_changed, sender=RRuleSchedule)
signals.post_save.connect(
    PeriodicTasks.update_changed, sender=RRuleSchedule)