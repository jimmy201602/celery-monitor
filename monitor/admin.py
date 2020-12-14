from django.contrib import admin
# Register your models here.
from djcelery.models import IntervalSchedule, CrontabSchedule
from .models import ActionLog

admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)


class custom_interval_admin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True


class custom_crontab_admin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True


class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'action', 'datetime']

    def get_username(self, obj):
        return obj.user.username


admin.site.register(ActionLog, ActionLogAdmin)
admin.site.register(IntervalSchedule, custom_interval_admin)
admin.site.register(CrontabSchedule, custom_crontab_admin)
