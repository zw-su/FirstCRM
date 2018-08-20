from zwAdmin.sites import site
from crm import models
from zwAdmin.BaseZwAdmin import BaseZwAdmin


class CustomerAdmin(BaseZwAdmin):
    list_display = ['name', 'source', 'contact',
                    'consultant', 'status', 'date']
    list_filter = ['source', 'consultant', 'status', 'date']
    search_fields = ['contact', 'consultant__name']
    readonly_fields = ['status', 'contact']
    filter_horizontal = ['咨询课程', ]
    actions = ['aaaaa']

    def aaaaa(self, request, queryset):
        return queryset.update(status=1)


site.register(models.CustomerInfo, CustomerAdmin)
site.register(models.UserProfile)
site.register(models.Role)