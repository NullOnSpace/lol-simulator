from django.contrib import admin
from .models import (Champion, ManaResource, EnergyResource, EmptyResource,
                     BasicItem, AdvancedItem, FinishedItem, StarterItem)


# Register your models here.
admin.site.register(Champion)
admin.site.register(ManaResource)
admin.site.register(EnergyResource)
admin.site.register(EmptyResource)
admin.site.register(BasicItem)
admin.site.register(AdvancedItem)
admin.site.register(FinishedItem)
admin.site.register(StarterItem)
