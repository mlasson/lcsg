from django.contrib import admin
from browser.models import Period, Letter, Family, Word, Occurrence, Cache

# Register your models here.
admin.site.register(Period)
admin.site.register(Letter)
admin.site.register(Family)
admin.site.register(Word)
admin.site.register(Occurrence)
admin.site.register(Cache)

