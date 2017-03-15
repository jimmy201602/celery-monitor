from django.conf import settings
from celery.app.control import Control
from celery import current_app
#app = current_app._get_current_object()
from .utils import nested_method,import_object
import datetime
from .singleton import Singleton

class CeleryClient(Singleton):
	_control = None

	def __init__(self):
		self._routes = getattr(settings, 'CELERY_ROUTES', {})
		
	@property
	def application(self):
		return current_app

	#@property
	def default_queue(self):
		return self.application.amqp.default_queue.name

	@property
	def routes(self):
		return self._routes
	
	@property
	def queues(self):
		return current_app.amqp.queues
	
	@property
	def _inspect(self):
		return self.application.control.inspect()
	
	@property
	def worker_stats(self):
		return self._inspect.stats()

	@property
	def enable_events(self):
		self.application.control.enable_events()
	
	@property	
	def disable_events(self):
		self.application.control.disable_events()

	def workers(self):
		response = self._inspect.stats()
		if not response:
			return []
		statuses = self.worker_statuses()
		queues = self.active_queues()
		if not queues:
			return []
		workers = []
		if isinstance(statuses,dict):
			for name, info in response.iteritems():
				worker = dict()
				worker['name'] = name
				#print statuses[name]
				#worker['status'] = statuses[worker['name']]
				#print 'name',name
				worker['status'] = statuses[name]
				#print worker.items()
				worker['concurrency'] = info['pool']['max-concurrency']
				worker['broker'] = {'transport': info['broker']['transport'],
								    'hostname': info['broker']['hostname'],
								    'port': info['broker']['port']}
				worker['complete'] = sum([v for v in info['total'].itervalues()])
				worker['queues'] = [i['name'] for i in queues[name]]
				#worker['queues'] = [1,2,3]
				workers.append(worker)
		return workers

	def worker_statuses(self):
		"""
		get worker statuses
		:return:
		"""
		response = self._inspect.ping()
		if not response:
			return []
		workers = {}
		for k, v in response.iteritems():
			for k_inner, v_inner in v.iteritems():
				if k_inner == 'ok' and v_inner == 'pong':
					workers[k] = 'Active'
				else:
					workers[k] = 'Passive'
				break
		return workers

	def active_queues(self):
		"""

		get queue mappings with workers
		:return:
		"""
		response = self._inspect.active_queues()
		if not response:
			return []
		return response

	def registered_tasks(self):
		"""
		get registered task list
		:return:
		"""
		response = self._inspect.registered()
		if not response:
			return []
		all_tasks = set()
		for worker, tasks in response.iteritems():
			for task in tasks:
				all_tasks.add(task.split('[')[0])

		registered_tasks = {}
		for task in all_tasks:
			if task in self.routes:
				queue = self.routes[task].get('queue', self.default_queue)
			else:
				queue = self.default_queue
			registered_tasks[task] = queue
		return registered_tasks

	def worker_registered_tasks(self):
		'''
		get worker registered task list
		'''
		response = self._inspect.registered_tasks()
		new_response = dict()
		for worker_name,all_tasks in response.items():
			registered_tasks = list()
			for task in all_tasks:
				if task in self.routes:
					queue = self.routes[task].get('queue', self.default_queue)
				else:
					queue = self.default_queue
				registered_tasks.append({'task_name':task.split('[')[0],'queue':queue})
			new_response[worker_name]=registered_tasks
		return new_response

	def active_tasks(self):
		"""
		get active tasks which is running currently
		:return:
		"""
		response = self._inspect.active()
		if not response:
			return {}
		for worker in response.keys():
			for tasks in response[worker]:
				tasks['time_start'] = datetime.datetime.fromtimestamp(tasks['time_start']).strftime('%Y-%m-%d %H:%M:%S.%f')
		return response

	def reserved_tasks(self):
		"""
		get reserved tasks which is in queue but still waiting to be executed
		:return:
		"""

		response = self._inspect.reserved()
		if not response:
			return {}
		for worker in response.keys():
			for tasks in response[worker]:
				if tasks['time_start'] is not None:
					tasks['time_start'] = datetime.datetime.fromtimestamp(tasks['time_start']).strftime('%Y-%m-%d %H:%M:%S.%f')
		return response

	def revoked_tasks(self):
		"""
		get revoked tasks
		:return:
		"""

		response = self._inspect.revoked()
		if not response:
			return {}
		#for worker in response.keys():
			#for tasks in response[worker]:
				#if tasks['time_start'] is not None:
					#tasks['time_start'] = datetime.datetime.fromtimestamp(tasks['time_start']).strftime('%Y-%m-%d %H:%M:%S.%f')
		return response

	def scheduled_tasks(self):
		"""
		get revoked tasks
		:return:
		"""

		response = self._inspect.scheduled()
		if not response:
			return {}
		#for worker in response.keys():
			#for tasks in response[worker]:
				#if tasks['time_start'] is not None:
					#tasks['time_start'] = datetime.datetime.fromtimestamp(tasks['time_start']).strftime('%Y-%m-%d %H:%M:%S.%f')
		return response  

	def execute(self, command, parameter):

		def run(*args):
			ctrl = args[0]
			task_name = args[1]['task_name']
			response = ctrl.app.send_task(task_name,reply=True,)
			return {'status':'success','message':'Task %s has been assigned task id is %s.' %(task_name,response)}

		def revoke(*args):
			ctrl = args[0]
			task_id = args[1]['task_id']
			destination = args[1]['destination']
			response = ctrl.revoke(task_id, terminate=True, signal="SIGKILL",reply=True,)
			if 'ok' in response[0][destination] and 'tasks unknown' not in response[0][destination]['ok']:
				response = {'status':'success','message':'Task %s on server %s has been revoked.' %(task_id,destination)}
			else:
				response = {'status':'failure','message':'Task %s on server %s does not exist.' %(task_id,destination)}
			return response

		def terminate(*args):
			ctrl = args[0]
			task_id = args[1]['task_id']
			destination = args[1]['destination']
			response = ctrl.revoke(task_id, terminate=True, signal="SIGTERM",reply=True,destination=[destination,],)
			if 'ok' in response[0][destination] and 'tasks unknown' not in response[0][destination]['ok']:
				response = {'status':'success','message':'Task %s on server %s has been terminated.' %(task_id,destination)}
			else:
				response = {'status':'failure','message':'Task %s on server %s does not exist.' %(task_id,destination)}
			return response

		def rate_limit(*args):
			ctrl = args[0]
			taskname = args[1]['task_name']
			ratelimit = args[1]['ratelimit']
			destination = args[1]['destination']
			response = ctrl.rate_limit(taskname,
						               ratelimit,
						               reply=True,
							destination=[destination])
			if len(response) != 0 and response[0][destination].has_key('ok'):
				response = {'status':'success','message':'%s' %(response[0][destination]['ok'])}
			elif len(response) != 0 and response[0][destination].has_key('error'):
				response = {'status':'failure','message':'%s' %(response[0][destination]['error'])}
			elif len(response) == 0:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.' }
			return response

		def add_consumer(*args):
			ctrl = args[0]
			destination = args[1]['destination']	
			queue = args[1]['queue']	
			response = ctrl.broadcast('add_consumer',
			                          arguments={'queue': queue},
			                          destination=[destination],
			                          reply=True)
			if response and 'ok' in response[0][destination]:
				response = {'status':'success','message':'%s' %(response[0][destination]['ok'])}
			else:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.'}
			return response

		def cancel_consumer(*args):
			ctrl = args[0]
			destination = args[1]['destination']	
			queue = args[1]['queue']	
			response = ctrl.broadcast('cancel_consumer',
			                          arguments={'queue': queue},
			                          destination=[destination],
			                          reply=True)
			if response and 'ok' in response[0][destination]:
				response = {'status':'success','message':'%s' %(response[0][destination]['ok'])}
			else:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.'}
			return response

		def shutdown(*args):
			ctrl = args[0]
			destination = args[1]['destination']
			response = ctrl.broadcast('shutdown', 
			                          destination=[destination],
			                          reply=True)
			response = {'status':'success','message':'Worker on %s will shutdown.' %(destination)}
			return response

		def restart(*args):
			ctrl = args[0]
			destination = args[1]['destination']
			response = ctrl.broadcast('pool_restart',
			                          arguments={'reload': True},
			                          destination=[destination],
			                          reply=True)
			if response and 'ok' in response[0][destination]:
				response = {'status':'success','message':'Worker on %s reload started.' %(destination)}
			elif response and 'error' in response[0][destination]:
				response = {'status':'failure','message':'Worker on %s reload failure. Reason:%s' %(destination,response[0][destination]['error'])}
			else:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.' }
			return response

		def ping(*args):
			ctrl = args[0]
			destination = args[1]['destination']
			response = ctrl.ping(destination=[destination],timeout=1.0)
			if response and 'ok' in response[0][destination]:
				response = {'status':'success','message':'Server %s is online.' %(destination)}
			else:
				response = {'status':'failure','message':'Server %s is offline.' %(destination)}
			return response
		
		def time_limit(*args):
			ctrl = args[0]
			taskname = args[1]['task_name']
			method = args[1]['method']
			destination = args[1]['destination']
			if method == 'soft':
				soft = int(args[1]['time_limit_soft'])
				response = ctrl.time_limit(taskname,
								           soft=soft,
								           reply=True,
								           destination=[destination])  				
			else:
				hard = int(args[1]['time_limit_hard'])
				response = ctrl.time_limit(taskname,
								           hard=hard,
								           reply=True,
								           destination=[destination])  				
			if len(response) != 0 and response[0][destination].has_key('ok'):
				response = {'status':'success','message':'%s' %(response[0][destination]['ok'])}
			elif len(response) != 0 and response[0][destination].has_key('error'):
				response = {'status':'failure','message':'%s' %(response[0][destination]['error'])}
			elif len(response) == 0:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.' }
			return response

		def autoscale(*args):
			ctrl = args[0]
			min_num = int(args[1]['min_num'])
			max_num = int(args[1]['max_num'])
			destination = args[1]['destination']
			response = ctrl.broadcast('autoscale',
						              arguments={'min': min_num, 'max': max_num},
						              destination=[destination],
						              reply=True)
			if len(response) != 0 and response[0][destination].has_key('ok'):
				response = {'status':'success','message':'%s' %(response[0][destination]['ok'])}
			elif len(response) != 0 and response[0][destination].has_key('error'):
				response = {'status':'failure','message':'%s' %(response[0][destination]['error'])}
			elif len(response) == 0:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.' }
			return response

		def poolgrow(*args):
			ctrl = args[0]
			grown_num = int(args[1]['grown_num'])
			destination = args[1]['destination']
			response = ctrl.pool_grow(n=grown_num, reply=True,
						              destination=[destination])
			if len(response) != 0 and response[0][destination].has_key('ok') and 'pool will grow' in response[0][destination]['ok']:
				response = {'status':'success','message':'Pool on server %s will grow %d pool.' %(destination,grown_num)}
			elif len(response) != 0 and response[0][destination].has_key('error'):
				response = {'status':'failure','message':'Parameter or errors happen, Please check,reason:%s' %response[0][destination]['error'] }
			else:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.' }
			return response

		def poolshrink(*args):
			ctrl = args[0]
			shrink_num = int(args[1]['shrink_num'])
			destination = args[1]['destination']					
			response = ctrl.pool_shrink(n=shrink_num, reply=True,
						                destination=[destination]) 
			if len(response) != 0 and response[0][destination].has_key('error') and 'Can\'t shrink pool. All processes busy!' in response[0][destination]['error']:
				response = {'status':'failure','message':'Can\'t shrink pool. All processes busy on server %s! Please try this later.' %(destination)}
			elif len(response) != 0 and response[0][destination].has_key('ok') and 'pool will shrink' in response[0][destination]['ok']:
				response = {'status':'success','message':'pool on server %s will shrink %d pool.' %(destination,shrink_num)}
			elif len(response) != 0 and response[0][destination].has_key('error'):
				response = {'status':'failure','message':'Parameter or errors happen, Please check. Reason:%s' %(response[0][destination]['error'])}
			else:
				response = {'status':'failure','message':'Parameter or errors happen, Please check.' }
			return response

		control = current_app.control
		nested = nested_method(self, 'execute', command)
		return nested(*(control, parameter))