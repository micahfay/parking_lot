from datetime import datetime

import pytz
from django.db import models

class ParkingLot(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False,
                            unique=True)
    def __str__(self):
        return self.name


class VehicleTypes(models.IntegerChoices):
    MOTORCYCLE = 1, 'Motorcycle'
    CAR = 2, 'Car'
    VAN = 3, 'Van'


class Vehicle(models.Model):
    type = models.IntegerField(choices=VehicleTypes.choices)
    license_plate = models.CharField(max_length=10, unique=True)
    parked_at = models.DateTimeField(
        default=lambda: datetime.now(tz=pytz.UTC))

    def __str__(self):
        return f'{VehicleTypes(self.type).name} - {self.license_plate}'


class SpaceTypes(models.IntegerChoices):
    MOTORCYCLE = 1, 'Motorcycle'
    CAR = 2, 'Car'
    VAN = 3, 'Van'


class ParkingSpace(models.Model):
    type = models.IntegerField(choices=SpaceTypes.choices)
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    number = models.IntegerField()
    previous = models.OneToOneField(
        'self', null=True, related_name='next', on_delete=models.CASCADE,
        default=None)

    class Meta:
        unique_together = ('lot', 'number')

    def __str__(self):
        return f'{self.lot.name} - {self.number}'
