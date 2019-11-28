from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from scheduler.models import *
import argparse
from dateutil.rrule import (
    rrule as dateutil_rrule,
    YEARLY,
    MONTHLY,
    WEEKLY,
    DAILY,
    HOURLY,
    MINUTELY,
    SECONDLY
)
from datetime import datetime
now = datetime.now()
today_weekday = now.isoweekday() - 1
hour = now.hour
minute =  now.minute
if minute < 58:
    minute =  datetime.now().minute + 1
else:
    hour = hour +1
    minute = 0
seconds  =  0 
month = datetime.now().month
day = datetime.now().day

schedule_class = RRuleSchedule

class Command(BaseCommand):
    help = 'Make an existing user as admin'


    def handle(self, *args, **kwargs):
        #Daily, for 10 occurrences.
        import pdb; pdb.set_trace()
        daily_by_count = schedule_class(DAILY, count=10)
        print(daily_by_count.get_all_runs)

        #Daily,  until December 24, 2022
        daily_by_untill = schedule_class(DAILY,ends_on= datetime(2022, 12, 24))

        #Daily,  Infinite
        daily_by_infinite = schedule_class(DAILY)

        #every_third_day
        every_third_day =  schedule_class(DAILY,inter=3)

        #weekly_count
        weekly_by_count = schedule_class(WEEKLY, count=10)

        #weekly_untill
        weekly_untill = schedule_class(WEEKLY,ends_on= datetime(2022, 12, 24))

        #weekly__infinite
        weekly__infinite = schedule_class(WEEKLY)

        #every_third_week_monday
        every_third_week_monday = schedule_class(WEEKLY,inter=3,byweekday=0)


        first_firday_every_month =  schedule_class(MONTHLY,byweekday=dateutil_rrule.FR(1))

        #Every other month on the 1st and last Sunday of the month 
        monthly_first_last_sunday = schedule_class(MONTHLY, inte=2, 
             byweekday=(dateutil_rrule.SU(1), dateutil_rrule.SU(-1)),
        )

        monthly_last_day = schedule_class(MONTHLY,  
             bymonthday=(-1,1,),
        )





# weekly = RRuleSchedule(frequency=WEEKLY,byhour=8,byminute=55,byweekday=2)
# weekly = RRuleSchedule(frequency=WEEKLY,byhour=8,byminute=55,byweekday=2)