
class BaseZwAdmin(object):
    def __init__(self):
        self.actions.extend(self.del_actions)
    list_display = []
    list_filter = []
    search_fields = []
    readonly_fields = []
    filter_horizontal = []
    actions = []
    del_actions = ['del_all_objs']

    def del_all_objs(self, request, queryset):

        return