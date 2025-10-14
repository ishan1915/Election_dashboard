from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(ElectionResult)
admin.site.register(State)
admin.site.register(Constituency)
admin.site.register(Party)
admin.site.register(ElectionYear)
admin.site.register(Candidate)