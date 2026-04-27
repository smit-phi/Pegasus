from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name               = "apps.users"

    def ready(self):
        # ready() is called once when Django finishes loading all apps.
        # Importing signals here is the standard pattern to register them.
        #
        # Why not import at the top of models.py or anywhere else?
        #   Django's app registry isn't fully loaded when models.py is first
        #   imported — importing signals there can cause AppRegistryNotReady
        #   errors. ready() is guaranteed to run after everything is loaded.
        #
        # The import itself is what registers the @receiver decorators —
        # until signals.py is imported, those decorators do nothing.
        import apps.users.signals  # noqa: F401
