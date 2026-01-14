from django.apps import AppConfig


class BoardConfig(AppConfig):
    name = 'board'

    def ready(self):
        import board.signals