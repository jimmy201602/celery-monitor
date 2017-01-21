from django.conf.urls import patterns, include, url
from djcelery.models import TaskState
from djcelery.admin import TaskMonitor
from .sites import site
from django.contrib.admin.views.main import ChangeList
from monitor.views import (
    workers,tasks,active_tasks,active_queues,reserved_tasks,
    queues_configuration,workers_index,registered_tasks_index,
    active_tasks_index,reserved_tasks_index,task_configuration,
    pool_configuration,worker_status,operations,periodictaskcreate,
    periodictaskupdate,periodictasklist,periodictaskdetail,
    periodictaskdelete,intervalcreate,crontabcreate,taskstatedetail)
urlpatterns = [
    
    url(r'^workers/$', workers.as_view(),name='workers'),
    url(r'^tasks/$', tasks.as_view(),name='tasks'),
    url(r'^active_tasks/$', active_tasks.as_view(),name='active_tasks'),
    url(r'^active_queues/$', active_queues.as_view(),name='active_queues'),
    url(r'^reserved_tasks/$', reserved_tasks.as_view(),name='reserved_tasks'),
    url(r'^queues_configuration/$', queues_configuration.as_view(),name='queues_configuration'),
    url(r'^workers_index/$', workers_index.as_view(),name='workers_index'),
    url(r'^registered_tasks_index/$', registered_tasks_index.as_view(),name='registered_tasks_index'),
    url(r'^active_tasks_index/$', active_tasks_index.as_view(),name='active_tasks_index'),
    url(r'^reserved_tasks_index/$', reserved_tasks_index.as_view(),name='reserved_tasks_index'),
    url(r'^task_configuration/$', task_configuration.as_view(),name='task_configuration'),
    url(r'^pool_configuration/$', pool_configuration.as_view(),name='pool_configuration'),
    url(r'^worker_status/$', worker_status.as_view(),name='worker_status'),
    url(r'^operations/$', operations.as_view(),name='operations'),
    #url(r'^conf/$', conf.as_view(),name='conf'),
    url(r'^periodictask/add/$', periodictaskcreate.as_view(), name='periodictask_add'),
    url(r'^periodictask/(?P<pk>[0-9]+)/update/$', periodictaskupdate.as_view(), name='periodictask_update'),
    url(r'^periodictask/$', periodictasklist.as_view(), name='periodictask_list'),
    url(r'^periodictask/(?P<pk>[0-9]+)/$', periodictaskdetail.as_view(),name="periodictask_detail"),
    url(r'^periodictask/(?P<pk>[0-9]+)/delete/$', periodictaskdelete.as_view(), name='periodictask_delete'),
    url(r'^interval/add/$', intervalcreate.as_view(), name='interval_add'),
    url(r'^crontab/add/$', crontabcreate.as_view(), name='crontab_add'),  
    url(r'^taskstate/(?P<pk>[0-9]+)/$', taskstatedetail.as_view(), name='taskstatedetail'),  
]

class Mychangelist(ChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return '/monitor/taskstate/%d/' %(pk)
    
class permission_modify(TaskMonitor):
    change_list_template = 'change_list.html'
    list_per_page = 15
    actions = None
    #list_filter = None
    def has_module_permission(self, request):
        return True
    def get_changelist(self, request, **kwargs):
        return Mychangelist
    def has_change_permission(self, request, obj=None):
        return True
site.register(TaskState,permission_modify)

urlpatterns += [
    url(r'', include(site.urls)),
]