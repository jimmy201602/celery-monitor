import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'celerymonitor.settings'
import django
from django.conf import settings
django.setup()
from djcelery.snapshot import Camera
from celery.utils.log import get_logger
from celery import Celery
import traceback
logger = get_logger(__name__)
import datetime
from djcelery.utils import DATABASE_ERRORS

class CeleryprojMonitorCamera(Camera):
    
    """
    This function is aim to  fix the bug when database encounter server domain name exchange, the monitor process 
    can't handle database lost exception. 
    """    
    def on_shutter(self, state, commit_every=5):

        def _handle_tasks():
            for i, task in enumerate(state.tasks.items()):
                self.handle_task(task)
        
        try:
            for worker in state.workers.items():
                self.handle_worker(worker)
        except DATABASE_ERRORS:
            print ('database error',datetime.datetime.now())
            logger.error(traceback.print_exc())
            from django.db import connection
            connection.close()             
            
        try:
            _handle_tasks()
        except DATABASE_ERRORS:
            print({'subject':'Mysql database encounter exchange','detail':str(traceback.print_exc())})
            print (datetime.datetime.now())
            logger.error(traceback.print_exc())
            from django.db import connection
            connection.close() 

            
def main(app, freq=1.0):
    state = app.events.State()
    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={'*': state.event})
        with CeleryprojMonitorCamera(state, freq=freq):
            recv.capture(limit=None, timeout=None)
        
if __name__ == '__main__':
    app = Celery(broker=getattr(settings,'BROKER_URL'))
    main(app)
