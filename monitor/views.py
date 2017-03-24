from django.shortcuts import render
from django.views.generic import View,TemplateView
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
# Create your views here.
from .login_api import LoginRequiredMixin
try:
    import simplejson as json
except ImportError:
    import json
from client import CeleryClient
from djcelery.admin import PeriodicTaskForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from djcelery.models import IntervalSchedule,CrontabSchedule,PeriodicTask,TaskState
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.db import models
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from celery import current_app
from django.db.models import Max,Count
import time
from django.utils.timezone import localtime

class workers(LoginRequiredMixin,View):
    def get(self,request):
        instance=CeleryClient()
        response = instance.workers()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass
    
class tasks(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.registered_tasks()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass
    
class active_tasks(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_tasks()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass

class reserved_tasks(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.reserved_tasks()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass

class active_queues(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_queues()
        if not response:
            return HttpResponse(json.dumps([]),content_type="application/json")
        else:
            return HttpResponse(json.dumps(response),content_type="application/json")
    def post(self,request):
        pass

class queues_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_queues()
        return render_to_response('queues_configuration.html',locals())
    def post(self,request):
        pass

class workers_index(LoginRequiredMixin,View):
    def get(self,request):
        import time
        a=time.time()
        instance = CeleryClient()
        b=time.time()
        response = instance.workers() 
        c=time.time()
        #print b - a
        #print c - b
        #print c - a
        #print response
        #from django.utils import translation
        #user_language = 'zh-hans'
        ###user_language = 'en'
        #translation.activate(user_language)
        #request.session[translation.LANGUAGE_SESSION_KEY] = user_language	        
        return render_to_response('workers.html',locals())
    
class registered_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.registered_tasks()
        return render_to_response('registered_tasks.html',locals())

class active_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_tasks()
        title = 'Active Tasks'
        action = 'terminate'
        return render_to_response('active_tasks.html',locals())

class reserved_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.reserved_tasks()
        title='Reserved Tasks'
        action = 'revoke'
        return render_to_response('active_tasks.html',locals())

class task_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.worker_registered_tasks()
        #print response
        return render_to_response('task_configuration.html',locals())

class worker_status(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        stats = instance.worker_stats
        #print stats
        active_tasks=instance.active_tasks()
        reserved_tasks=instance.reserved_tasks()
        revoked_tasks=instance.revoked_tasks()
        #print revoked_tasks
        scheduled_tasks=instance.scheduled_tasks()
        print active_tasks
        return render_to_response('worker_status.html',locals())
    
class pool_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        stats = instance.worker_stats
        return render_to_response('pool_configuration.html',locals())

class operations(LoginRequiredMixin,View):
    def get(self,request):
        command = self.request.GET.get('command','')
        parameter = json.loads(self.request.GET.get('parameter',''))
        #print 'get',self.request.GET
        #print 'command',command
        #print 'parameter',parameter
        instance = CeleryClient()
        response = instance.execute(command, parameter)
        return HttpResponse(json.dumps(response),content_type="application/json")

class periodictaskcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    form_class = PeriodicTaskForm
    template_name = 'periodictaskcreate.html'
    success_url = reverse_lazy('periodictask_list')
    success_message = "%(name)s was created successfully"
    model = PeriodicTask
    def get_form(self, form_class):
        form = super(periodictaskcreate, self).get_form(form_class)
        rel_model = form.Meta.model
        rel = rel_model._meta.get_field('crontab').rel
        irel = rel_model._meta.get_field('interval').rel
        form.fields['crontab'].widget = RelatedFieldWidgetWrapper(form.fields['crontab'].widget, rel, 
                                                                  admin.site, can_add_related=True, can_change_related=True)
        form.fields['interval'].widget = RelatedFieldWidgetWrapper(form.fields['interval'].widget, irel, 
                                                                   admin.site, can_add_related=True, can_change_related=True)          
        return form    

class periodictaskupdate(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    form_class = PeriodicTaskForm
    template_name = 'periodictaskupdate.html'
    success_url = reverse_lazy('periodictask_list')
    success_message = "%(name)s was updated successfully"
    model = PeriodicTask   
    def get_form(self, form_class):
        form = super(periodictaskupdate, self).get_form(form_class)
        rel_model = form.Meta.model
        rel = rel_model._meta.get_field('crontab').rel
        irel = rel_model._meta.get_field('interval').rel      
        form.fields['crontab'].widget = RelatedFieldWidgetWrapper(form.fields['crontab'].widget, rel, 
                                                                  admin.site, can_add_related=True, can_change_related=True)
        form.fields['interval'].widget = RelatedFieldWidgetWrapper(form.fields['interval'].widget, irel, 
                                                                   admin.site, can_add_related=True, can_change_related=True)        
        return form
    
class periodictasklist(LoginRequiredMixin,ListView):
    template_name = 'periodictasklist.html'
    def get_queryset(self):
        return PeriodicTask.objects.all()
    
class periodictaskdetail(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    form_class = PeriodicTaskForm
    template_name = 'periodictaskdetail.html'
    success_url = reverse_lazy('periodictask_list')
    success_message = "%(name)s was updated successfully"
    model = PeriodicTask

    
class periodictaskdelete(LoginRequiredMixin,DeleteView):
    template_name = 'periodictaskdelete.html'
    model = PeriodicTask
    success_url = reverse_lazy('periodictask_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        except Exception,e:
            print e
            messages.add_message(request, messages.ERROR, self.object.name + ' can not deleted because hosts use that ENV!')

        return HttpResponseRedirect(self.get_success_url())
    
class crontabcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'crontabcreate.html'
    success_url = reverse_lazy('crontab_add')
    success_message = "crontab was created successfully"
    model = CrontabSchedule
    fields=['minute','hour','day_of_week','day_of_month','month_of_year']

class intervalcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'intervalcreate.html'
    success_url = reverse_lazy('interval_add')
    success_message = "interval was created successfully"
    model = IntervalSchedule
    fields=['every','period']
  
class taskstatedetail(LoginRequiredMixin,DetailView):
    model = TaskState
    template_name = 'taskstatedetail.html'

class run_task(LoginRequiredMixin,View):
    def get(self,request):
        id = self.request.GET.get('id',None)
        name = self.request.GET.get('name',None)
        try:
            querry_res = PeriodicTask.objects.get(id=id,name=name)
            args = json.loads(querry_res.args)
            kwargs = json.loads(querry_res.kwargs)
            queue = querry_res.queue
            routing_key = querry_res.routing_key
            task_name = querry_res.task
        except ObjectDoesNotExist:
            response = {'status':'fail','message':'task name %s doesn\'t exits' %(name) }
            return HttpResponse(json.dumps(response),content_type="application/json")
        if queue == 'None' or queue == None:
            queue = 'celery'
        res = current_app.send_task(task_name,args=args,kwargs=kwargs,queue=queue,routing_key=routing_key)
        response = {'status':'success','message':'task name %s has been running,task id is %s' %(name,res.id) }    
        return HttpResponse(json.dumps(response),content_type="application/json")
    
class task_state_task_api(LoginRequiredMixin,View):
    def get(self,request):
        task_name = self.request.GET.get('task_name',None)
        def tstamp(object):
            return time.mktime(localtime(object.tstamp).timetuple())  * 1000
        data = [[tstamp(i),i.runtime] for i in TaskState.objects.filter(name=task_name).exclude(result__contains='running').order_by('tstamp') ]
        chart_data = {'name':task_name,'data':data}
        return HttpResponse(json.dumps(chart_data),content_type="application/json")
    
class task_state_sucess_rate_api(LoginRequiredMixin,View):
    def get(self,request):
        task_name = self.request.GET.get('task_name',None)
        data = list()
        [ data.append({'name':i['state'],'y':int(i['total']),}) for i in TaskState.objects.filter(name=task_name).values('state').annotate(total=Count('state')).order_by('total')]
        for i in data:
            if i['name'] == 'SUCCESS':
                i['color'] = '#66ff33' 
            elif i['name'] == 'FAILURE':
                i['color'] = 'red' 
        chart_data = {'name':task_name,'data':data}
        return HttpResponse(json.dumps(chart_data),content_type="application/json")

class task_state_max_runtime_api(LoginRequiredMixin,View):
    def get(self,request):
        data = list()
        task_name = list()
        [[data.append(i['max_runtime']),task_name.append(i['name'])] for i in TaskState.objects.values('name').annotate(max_runtime=Max('runtime')).order_by('-max_runtime')[:20]]
        return HttpResponse(json.dumps({'data':data,'task_name_cat':task_name}),content_type="application/json")

class task_state_failure_count_api(LoginRequiredMixin,View):
    def get(self,request):
        data = list()
        task_name = list()
        [[data.append(i['failure_count']),task_name.append(i['name'])] for i in TaskState.objects.values('name').filter(state='FAILURE').annotate(failure_count=Count('state')).order_by('-failure_count')]
        return HttpResponse(json.dumps({'data':data,'task_name_cat':task_name}),content_type="application/json")
    
class task_state_execute_count_api(LoginRequiredMixin,View):
    def get(self,request):
        task_name = self.request.GET.get('task_name',None)
        query = TaskState.objects.filter(name=task_name).values('state')
        failure_count = query.filter(state='FAILURE').count()
        execute_count = query.filter(state='SUCCESS').count()
        chart_data = {'name':task_name,'data':[failure_count,execute_count],'task_name_cat':['failure_count','execute_count']}
        return HttpResponse(json.dumps(chart_data),content_type="application/json")
    
class task_state_chart(LoginRequiredMixin,View):
    def get(self,request):
        task_name_list=TaskState.objects.order_by().values('name').distinct()
        print task_name_list
        return render_to_response('taskstatechart.html',locals())