from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from healthy_life_api import settings
from user.models import User
import decimal
import os


class Command(BaseCommand):
    help = 'running the server in test mode'

    def handle(self, *args, **kwargs):
        self._preparing_test_db()
        self._create_test_data()

    @staticmethod
    def _preparing_test_db():
        settings.DATABASES['default']['NAME'] = os.getenv('NAME_TEST_DB')

        try:
            call_command('flush', '--no-input')
        except CommandError:
            pass
        call_command('migrate')

    @staticmethod
    def _create_test_data():
        amount_test_user = 15
        common_part_of_usernames = 'user'
        common_part_of_password = 'qwnmfwkn2en2irnr2kd'

        users = [User(username=f'{common_part_of_usernames}_{i}',
                 password=make_password(f'{common_part_of_password}_{common_part_of_usernames}_{i}'),
                 email=f'{common_part_of_usernames}_{i}@mail.com',
                 balance=decimal.Decimal("99.99")) for i in range(1, amount_test_user + 1)]

        users.append(User(username='root',
                          password=make_password(f'{common_part_of_password}_root'),
                          email='root@mail.com',
                          is_superuser=True,
                          is_staff=True))

        for user in users:
            user.save()
