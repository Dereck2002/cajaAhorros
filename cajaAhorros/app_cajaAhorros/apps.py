from django.apps import AppConfig


class AppCajaahorrosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_cajaAhorros'
    def ready(self):
        from . import signals

