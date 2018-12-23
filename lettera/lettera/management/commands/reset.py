from django.core.management import call_command

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from lettera.settings import DATABASES, BASE_DIR
from os import listdir, mkdir, rename
from os.path import isfile, join, dirname, isdir, exists, basename

from datetime import datetime
class Command(BaseCommand):
    args = '<???>'
    help = 'Reset'

    def add_arguments(self, parser):
        parser.add_argument('fixture_directory', nargs=1)

    def handle(self, *args, **options):
        db_file = DATABASES['default']['NAME']
        backup_directory = join(BASE_DIR, '../backup')
        if not exists(backup_directory):
            mkdir(backup_directory)
        elif not isdir(backup_directory):
            raise CommandError("'{0}' is a valid directory".format(backup_directory))
        if exists(db_file):
            backup_file = join(backup_directory, datetime.now().strftime("%Y-%m-%d-%H-%M-%S-") + basename(db_file))
            rename(db_file, backup_file)
        directory = options['fixture_directory'][0]
        fixtures = [
            f for f in listdir(directory) if isfile(join(directory, f))
            and f.endswith('.json')
            ]
        call_command('migrate', "--run-syncdb")
        for fixture in fixtures:
            print("Loading fixture '{0}' ...".format(fixture))
            call_command('loaddata', join(directory, fixture))
        call_command('create_users')
        call_command('initdb')
        call_command('filter')
        call_command('precomp')
        call_command('frequency')
        call_command('corpus_period')
