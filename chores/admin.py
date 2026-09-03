from django.contrib import admin

from .models import Chore, ChoreAssignment, ChoreLog, Household, Person

admin.site.register(Household)
admin.site.register(Person)
admin.site.register(Chore)
admin.site.register(ChoreAssignment)
admin.site.register(ChoreLog)
