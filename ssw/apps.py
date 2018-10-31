from django.apps import AppConfig


class SswConfig(AppConfig):
    name = 'ssw'

    def ready(self):
        import ssw.signals
