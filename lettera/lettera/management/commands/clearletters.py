from django.core.management.base import BaseCommand
from browser.models import Letter

class Command(BaseCommand):
    args = '<???>'
    help = 'Remove letters'

    def handle(self, *args, **options):
        Letter.objects.all().delete()
