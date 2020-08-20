from apscheduler.schedulers.blocking import BlockingScheduler
import utils.downloads as downloadas
import os
sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=14)
def scheduled_job():
    downloads.daily_download()
    downloads.daily_upload()
    for filename in os.listdir('assets/'):
        if filename.endswith(".xls"):
            os.remove('assets/'+filename)
        elif filename.endswith(".csv"):
            os.remove('assets/'+filename)
        elif filename.endswith(".aspx"):
            os.remove('assets/'+filename)


sched.start()
