from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand
from healthy_life_api import settings
import sys
import os


class Command(BaseCommand):
    help = 'running the server in test mode'

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise Exception('test mode is available only in debug mode')

        settings.DATABASES['default']['NAME'] = os.getenv('NAME_TEST_DB')
        execute_from_command_line([sys.argv[0], 'runserver'])
