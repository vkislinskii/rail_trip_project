from django.contrib import admin
from core.models import Cities, TrainTrips, PointsOfInterest, RoutesDict

admin.site.register(Cities)
admin.site.register(TrainTrips)
admin.site.register(PointsOfInterest)
admin.site.register(RoutesDict)