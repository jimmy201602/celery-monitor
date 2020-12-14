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
import datetime
import ast
from rest_framework.views import APIView
from rest_framework.response import Response
from celerymonitor.celeryapp import app as celeryprojapp
from .models import ActionLog
from django.contrib.auth.models import User



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
        return render_to_response('monitor/queues_configuration.html',locals())
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
        # from django.utils import translation
        # user_language = 'zh-hans'
        ###user_language = 'en'
        # translation.activate(user_language)
        # request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        return render_to_response('monitor/workers.html',locals())

class registered_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.registered_tasks()
        return render_to_response('monitor/registered_tasks.html',locals())

class active_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.active_tasks()
        title = 'Active Tasks'
        action = 'terminate'
        return render_to_response('monitor/active_tasks.html',locals())

class reserved_tasks_index(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.reserved_tasks()
        title='Reserved Tasks'
        action = 'revoke'
        return render_to_response('monitor/active_tasks.html',locals())

class task_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        response = instance.worker_registered_tasks()
        return render_to_response('monitor/task_configuration.html',locals())

class worker_status(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        stats = instance.worker_stats
        active_tasks=instance.active_tasks()
        reserved_tasks=instance.reserved_tasks()
        revoked_tasks=instance.revoked_tasks()
        scheduled_tasks=instance.scheduled_tasks()
        return render_to_response('monitor/worker_status.html',locals())

class pool_configuration(LoginRequiredMixin,View):
    def get(self,request):
        instance = CeleryClient()
        stats = instance.worker_stats
        return render_to_response('monitor/pool_configuration.html',locals())

class operations(LoginRequiredMixin,View):
    def get(self,request):
        command = self.request.GET.get('command','')
        parameter = json.loads(self.request.GET.get('parameter',''))
        instance = CeleryClient()
        response = instance.execute(command, parameter)
        return HttpResponse(json.dumps(response),content_type="application/json")

class periodictaskcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    form_class = PeriodicTaskForm
    template_name = 'monitor/periodictaskcreate.html'
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
    template_name = 'monitor/periodictaskupdate.html'
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
    template_name = 'monitor/periodictasklist.html'
    def get_queryset(self):
        return PeriodicTask.objects.all()

class periodictaskdetail(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    form_class = PeriodicTaskForm
    template_name = 'monitor/periodictaskdetail.html'
    success_url = reverse_lazy('periodictask_list')
    success_message = "%(name)s was updated successfully"
    model = PeriodicTask


class periodictaskdelete(LoginRequiredMixin,DeleteView):
    template_name = 'monitor/periodictaskdelete.html'
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
    template_name = 'monitor/crontabcreate.html'
    success_url = reverse_lazy('crontab_add')
    success_message = "crontab was created successfully"
    model = CrontabSchedule
    fields=['minute','hour','day_of_week','day_of_month','month_of_year']

class intervalcreate(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'monitor/intervalcreate.html'
    success_url = reverse_lazy('interval_add')
    success_message = "interval was created successfully"
    model = IntervalSchedule
    fields=['every','period']

class taskstatedetail(LoginRequiredMixin,DetailView):
    model = TaskState
    template_name = 'monitor/taskstatedetail.html'

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

class RunTaskApi(APIView):
    def post(self,request,format=None):
        name = self.request.data.get('name',None)
        args = self.request.data.get('args',None)
        kwargs = self.request.data.get('kwargs',None)
        queue = self.request.data.get('queue',None)
        if args is not None:
            if not isinstance(args,list):
                try:
                    args = json.loads(args)
                except Exception,e:
                    args = args
        if kwargs is not None:
            try:
                kwargs = json.loads(kwargs)
            except Exception,e:
                kwargs = kwargs
        try:
            querry_res = PeriodicTask.objects.get(name=name)
            if args is None:
                args = json.loads(querry_res.args)
            else:
                args.extend(json.loads(querry_res.args))
            if kwargs is None:
                kwargs = json.loads(querry_res.kwargs)
            else:
                kwargs.update(kwargs)
            if queue is None:
                queue = querry_res.queue
            routing_key = querry_res.routing_key
            task_name = querry_res.task
        except ObjectDoesNotExist:
            response = {'status':False,'message':'task name %s doesn\'t exits' %(name) }
            ActionLog.objects.create(user=User.objects.get(username=self.request.user),action='run task',detail=json.dumps(self.request.data))
            return Response(response)
        if queue == 'None' or queue == None:
            queue = 'celery'
        res = celeryprojapp.send_task(task_name,args=args,kwargs=kwargs,queue=queue,routing_key=routing_key)
        response = {'status':True,'message':'task name %s has been running,task id is %s' %(name,res.id) }
        try:
            ActionLog.objects.create(user=User.objects.get(username=self.request.user),action='run task',detail=json.dumps({'request':self.request.data,'task_nmae':name,'task':task_name}))
        except Exception,e:
            print e
        return Response(response)

class task_state_task_api(LoginRequiredMixin,View):
    def get(self,request):
        task_name = self.request.GET.get('task_name',None)
        start_time = self.request.GET.get('start_time',(datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')) 
        end_time = self.request.GET.get('end_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))   
        def tstamp(object):
            return time.mktime(localtime(object.tstamp).timetuple())  * 1000
        data = [[tstamp(i),i.runtime] for i in TaskState.objects.filter(tstamp__range=[start_time,end_time]).filter(name=task_name).exclude(result__contains='running').order_by('tstamp') ]
        chart_data = {'name':task_name,'data':data}
        return HttpResponse(json.dumps(chart_data),content_type="application/json")

class task_state_sucess_rate_api(LoginRequiredMixin,View):
    def get(self,request):
        task_name = self.request.GET.get('task_name',None)
        start_time = self.request.GET.get('start_time',(datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'))
        end_time = self.request.GET.get('end_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))        
        data = list()
        [ data.append({'name':i['state'],'y':int(i['total']),}) for i in TaskState.objects.filter(tstamp__range=[start_time,end_time]).filter(name=task_name).values('state').annotate(total=Count('state')).order_by('total')]
        for i in data:
            if i['name'] == 'SUCCESS':
                i['color'] = '#66ff33'
            elif i['name'] == 'FAILURE':
                i['color'] = 'red'
        chart_data = {'name':task_name,'data':data}
        return HttpResponse(json.dumps(chart_data),content_type="application/json")

class task_state_max_runtime_api(LoginRequiredMixin,View):
    def get(self,request):
        start_time = self.request.GET.get('start_time',(datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'))
        end_time = self.request.GET.get('end_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))        
        data = list()
        task_name = list()
        [[data.append(i['max_runtime']),task_name.append(i['name'])] for i in TaskState.objects.filter(tstamp__range=[start_time,end_time]).values('name').annotate(max_runtime=Max('runtime')).order_by('-max_runtime')[:20]]
        return HttpResponse(json.dumps({'data':data,'task_name_cat':task_name}),content_type="application/json")

class task_state_failure_count_api(LoginRequiredMixin,View):
    def get(self,request):
        task_name = self.request.GET.get('task_name',None)
        start_time = self.request.GET.get('start_time',(datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'))
        end_time = self.request.GET.get('end_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))        
        data = list()
        task_name = list()
        [[data.append(i['failure_count']),task_name.append(i['name'])] for i in TaskState.objects.values('name').filter(tstamp__range=[start_time,end_time]).filter(state='FAILURE').annotate(failure_count=Count('state')).order_by('-failure_count')]
        return HttpResponse(json.dumps({'data':data,'task_name_cat':task_name}),content_type="application/json")

class task_state_execute_count_api(LoginRequiredMixin,View):
    def get(self,request):
        start_time = self.request.GET.get('start_time',(datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'))
        end_time = self.request.GET.get('end_time',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))        
        task_name = self.request.GET.get('task_name',None)
        query = TaskState.objects.filter(tstamp__range=[start_time,end_time]).filter(name=task_name).values('state')
        failure_count = query.filter(state='FAILURE').count()
        execute_count = query.filter(state='SUCCESS').count()
        chart_data = {'name':task_name,'data':[failure_count,execute_count],'task_name_cat':['failure_count','execute_count']}
        return HttpResponse(json.dumps(chart_data),content_type="application/json")

class task_state_chart(LoginRequiredMixin,View):
    def get(self,request):
        start_time = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')             
        task_name_list=TaskState.objects.order_by().values('name').distinct()
        return render_to_response('monitor/taskstatechart.html',locals())