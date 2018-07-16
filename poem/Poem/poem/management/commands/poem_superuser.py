from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from Poem.settings import SUPERUSER_NAME, SUPERUSER_PASS, SUPERUSER_EMAIL
from django.db import DEFAULT_DB_ALIAS
from django.db.utils import IntegrityError

# based on django/contrib/auth/management/commands/createsuperuser.py


class Command(BaseCommand):
    help = 'Used to create a superuser.'
    requires_migrations_checks = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()

    def handle(self, *args, **kwargs):
        user_data = dict()

        user_data[self.UserModel.USERNAME_FIELD] = SUPERUSER_NAME
        user_data['password'] = SUPERUSER_PASS
        user_data['email'] = SUPERUSER_EMAIL

        try:
            self.UserModel._default_manager.db_manager(DEFAULT_DB_ALIAS).create_superuser(**user_data)
            self.stdout.write("Superuser created successfully.")
        except IntegrityError:
            self.stderr.write("Superuser already created.")
