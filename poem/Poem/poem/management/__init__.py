from django.db.models import signals
from django.db.models.signals import post_syncdb
from django.contrib.auth import get_user
from django.contrib.auth import models as auth_models
from django.contrib.auth.management import create_superuser as default_create_superuser
import Poem.poem.models
import Poem.settings

username = getattr(Poem.settings, 'SUPERUSER_NAME', False)
password = getattr(Poem.settings, 'SUPERUSER_PASS', False)
email = getattr(Poem.settings, 'SUPERUSER_EMAIL', '')

if username and password:
    """
    Disable syncdb prompting for superuser creation.
    """
    signals.post_syncdb.disconnect(default_create_superuser,\
            sender=auth_models,\
            dispatch_uid="django.contrib.auth.management.create_superuser")

    def create_superuser_config(sender, **kwargs):
        print 'Creating superuser account: ' + username
        user, created = auth_models.User.objects.get_or_create(pk=1)
        if user:
            user.is_staff, user.is_active = True, True
            user.is_superuser = True
            user.set_password(password)
            user.username = username
            user.email = email
            user.save()

    signals.post_syncdb.connect(create_superuser_config, sender=auth_models)
