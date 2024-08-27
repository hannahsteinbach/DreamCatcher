from django.apps import AppConfig


class DreamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dreams'


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # add this
    def ready(self):
        import users.signals  # noqa
