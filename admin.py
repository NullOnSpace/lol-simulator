from django.contrib import admin
from .models import Champion, ManaResource, EnergyResource, EmptyResource


# Register your models here.
admin.site.register(Champion)
admin.site.register(ManaResource)
admin.site.register(EnergyResource)
admin.site.register(EmptyResource)
