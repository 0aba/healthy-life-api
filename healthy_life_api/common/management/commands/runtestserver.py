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
        usernames = ('user1', 'user2', 'user3',)
        common_part_of_password = 'qwnmfwkn2en2irnr2kd'
        for username in usernames:
            User.objects.create_user(username=username,
                                     password=f'{common_part_of_password}_{username}',
                                     email=f'{username}@mail.com')

        User.objects.create_superuser(username='root',
                                      password=f'{common_part_of_password}_root',
                                      email='root@mail.com')

    @staticmethod
    def _start_server():
        execute_from_command_line([sys.argv[0], 'runserver'])
