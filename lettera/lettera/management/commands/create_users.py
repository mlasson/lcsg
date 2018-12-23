from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


def create_superuser(name, mail, password):
    try:
        user = User.objects.create_superuser(name, mail, password)
        user.save()
    except Exception as e:
        print('While creating users, the following exception was caught :')
        print(e)

class Command(BaseCommand):
    def handle(self, *args, **options):
        create_superuser('cmanchio', '', 'marcelle')
        create_superuser('mlasson', '', 'passme')
