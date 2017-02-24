from django.core.management.base import BaseCommand
import logging
from redis import Redis
from rq_scheduler import Scheduler
from datetime import datetime
# from payment_released.models import ReleasePayment
# if uncomment then raise

logging.basicConfig(filename='payment_release.log', level=logging.INFO)


def check_release():
    print('TEST')
    logging.info(str(datetime.now()) + "TEST: {}".format('TEST'))


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.stdout.write('%s running payment release' % datetime.now(),
                          ending='\n')
        self.scheduler = Scheduler(connection=Redis('redis'))

    def handle(self, *args, **options):
        self.scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=check_release,
            interval=1,
            repeat=None
        )
