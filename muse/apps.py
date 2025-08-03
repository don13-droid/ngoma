from django.apps import AppConfig


class MuseConfig(AppConfig):
    name = 'muse'
    verbose_name = 'Muse'

    def ready(self):
        import muse.signals
