import re, logging, browser, sys
from django.core.management.base import BaseCommand, CommandError
from browser.models import Cache
from optparse import make_option
from itertools import tee
from collections import defaultdict


class Command(BaseCommand):
    args = '<???>'
    help = 'Clear the cache table'

    def handle(self, *args, **options):
        Cache.objects.all().delete()
