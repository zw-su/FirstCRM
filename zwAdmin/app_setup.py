from django import conf

def zwAdmin_auto_app():
    for my_app in conf.settings.INSTALLED_APPS:

        try:
            mod = __import__('%s.zwAdmin' % my_app)

        except ImportError:
            pass