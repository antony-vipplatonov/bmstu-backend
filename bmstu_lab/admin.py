from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Compaund)
admin.site.register(Ship)
admin.site.register(CompaundShips)
admin.site.register(Users)
