from django.contrib import admin

# Register your models here.
from djcelery.admin import TaskMonitor
class mytask(TaskMonitor):
	list_filter = ('state', 'name', 'tstamp', 'eta', 'worker')