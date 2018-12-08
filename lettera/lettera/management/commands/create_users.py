from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = '<???>'
    help = 'Compute inverse and direct frequencies'

    def handle(self, *args, **options):
        try:
            user = User.objects.create_user(
                'cmanchio', 'corinne.manchio@gmail.com', 'sauvageot')
            user.save()
        except Exception as e:
            print('While creating users, the following exception was caught :')
            print(e)
