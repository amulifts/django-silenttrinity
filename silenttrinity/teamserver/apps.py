from django.apps import AppConfig


class TeamserverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teamserver'

    def ready(self):
        """
        Initialize any app-specific configurations
        """
        pass