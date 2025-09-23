from django.apps import AppConfig


class InstructorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'instructors'

def ready(self):
    import your_app_name.signals
    from . import signals  # Ensure signals are imported when the app is ready
    signals.create_instructor_profile.connect(self.create_instructor_profile)