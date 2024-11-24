import decimal

from django.core.management import call_command, execute_from_command_line
from django.core.management.base import BaseCommand, CommandError
from healthy_life_api import settings
from user.models import User
import sys
import os


class Command(BaseCommand):
    help = 'running the server in test mode'

    def handle(self, *args, **kwargs):
        self._setup_test_database()
        self._create_test_data()
        self._start_server()

    @staticmethod
    def _setup_test_database():
        if not settings.DEBUG:
            raise Exception('test mode is available only in debug mode')

        settings.DATABASES['default']['NAME'] = os.getenv('NAME_TEST_DB')

        try:
            call_command('flush', '--no-input')
        except CommandError:
            pass
        call_command('migrate')

    @staticmethod
    def _create_test_data():
        amount_test_user = 3
        usernames = ('user1', 'user2', 'user3',)
        start_balances = (decimal.Decimal('0.00'), decimal.Decimal('100.00'), decimal.Decimal('1000.00'))
        common_part_of_password = 'qwnmfwkn2en2irnr2kd'
        for i in range(amount_test_user):
            User.objects.create_user(username=usernames[i],
                                     password=f'{common_part_of_password}_{usernames[i]}',
                                     email=f'{usernames[i]}@mail.com',
                                     balance=start_balances[i])

        User.objects.create_superuser(username='root',
                                      password=f'{common_part_of_password}_root',
                                      email='root@mail.com')

    @staticmethod
    def _start_server():
        execute_from_command_line([sys.argv[0], 'runserver'])
