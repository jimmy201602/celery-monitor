from django.contrib.admin.sites import AdminSite
from django.conf import settings
from functools import update_wrapper
from django.utils import six

class ModifyAdminsite(AdminSite):
    
    def has_permission(self, request):
        """
        Returns True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        if request.user.is_authenticated():
            return True
        return request.user.is_active and request.user.is_staff
    
    def get_urls(self):
        from django.conf.urls import url, include
        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.contenttypes.views imports ContentType.
        from django.contrib.contenttypes import views as contenttype_views

        if settings.DEBUG:
            self.check_dependencies()

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        #urlpatterns = [
            #url(r'^$', wrap(self.index), name='index'),
            #url(r'^login/$', self.login, name='login'),
            #url(r'^logout/$', wrap(self.logout), name='logout'),
            #url(r'^password_change/$', wrap(self.password_change, cacheable=True), name='password_change'),
            #url(r'^password_change/done/$', wrap(self.password_change_done, cacheable=True),
                #name='password_change_done'),
            #url(r'^jsi18n/$', wrap(self.i18n_javascript, cacheable=True), name='jsi18n'),
            #url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$', wrap(contenttype_views.shortcut),
                #name='view_on_site'),
        #]
        
        urlpatterns = []
        
        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        valid_app_labels = []
        for model, model_admin in six.iteritems(self._registry):
            urlpatterns += [
                url(r'^%s/' % (model._meta.model_name), include(model_admin.urls)),
                #url(r'^test/test/', include(model_admin.urls)),
            ]
            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        #print urlpatterns
        # If there were ModelAdmins registered, we should have a list of app
        # labels for which we need to allow access to the app_index view,
        if valid_app_labels:
            regex = r'^(?P<app_label>' + '|'.join(valid_app_labels) + ')/$'
            urlpatterns += [
                url(regex, wrap(self.app_index), name='app_list'),
            ]
        return urlpatterns

site = ModifyAdminsite()