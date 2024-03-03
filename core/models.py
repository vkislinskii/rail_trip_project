from django.db import models

# Create your models here.
class Cities(models.Model):
    city = models.CharField(max_length=40, blank=False)

    def __str__(self):
        return self.city

class TrainTrips(models.Model):
    city_id_from = models.IntegerField(default=0, blank=False)
    city_id_to = models.IntegerField(default=0, blank=False)
    departure_day = models.DateField(blank=False)
    arrival_day = models.DateField(blank=False)
    departure_time = models.CharField(max_length=5, blank=False)
    arrival_time = models.CharField(max_length=5, blank=False)
    price = models.CharField(max_length=5, blank=False)

    def __str__(self):
        return f'{self.city_id_from} {self.city_id_to} {self.departure_day} {self.departure_time}'

class PointsOfInterest(models.Model):
    city_id = models.IntegerField(default=0, blank=False)
    name = models.CharField(max_length=50, blank=False)
    address = models.CharField(max_length=50, blank=False)
    rating = models.CharField(max_length=3, blank=False)

    def __str__(self):
        return f'{self.city_id} {self.name}'

class RoutesDict(models.Model):
    city_id_from = models.IntegerField(default=0, blank=False)
    city_id_to = models.IntegerField(default=0, blank=False)

    def __str__(self):
        return f'{self.city_id_from} {self.city_id_to}'


