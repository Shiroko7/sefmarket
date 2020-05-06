from apscheduler.schedulers.blocking import BlockingScheduler
import downloads
import os
sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    downloads.daily_download()
    downloads.daily_upload()
    

sched.start()


