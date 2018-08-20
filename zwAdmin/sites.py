from zwAdmin.BaseZwAdmin import BaseZwAdmin


class Adminsite:
    def __init__(self):
        self.global_app = {}

    def register(self, models_class, admin_class=None):
        app_name = models_class._meta.app_label
        model_name = models_class._meta.model_name
        if app_name not in self.global_app:
            self.global_app[app_name] = {}
        if not admin_class:
            admin_class = BaseZwAdmin()
        else:
            admin_class = admin_class()

        admin_class.model = models_class
        self.global_app[app_name][model_name] = admin_class

site = Adminsite()