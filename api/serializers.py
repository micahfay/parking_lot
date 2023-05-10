from datetime import datetime

import pytz
from rest_framework import serializers, generics
from rest_framework.exceptions import ValidationError

from .models import ParkingLot, ParkingSpace, Vehicle, VehicleTypes, SpaceTypes


class ParkingLotSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    spaces = serializers.ListField(child=serializers.ChoiceField(
        choices=SpaceTypes.choices),
        help_text="Array of parking spots by type, 1 for a motorcycle spot, "
                  "2 for a car spot and 3 for a van spot", required=True)

    def save(self):

        spaces = self.validated_data['spaces']
        parking_lot = ParkingLot.objects.create(name=self.validated_data[
            'name'])
        previous = None
        for number, space in enumerate(spaces):
            current = ParkingSpace.objects.create(
                lot=parking_lot,
                number=number,
                type=SpaceTypes(space),
                previous=previous
            )
            previous = current
        return parking_lot


class ParkingLotQuerySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, help_text='the name of the '
                                                           'parking lot')


class ParkingLotStatusSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, help_text='the name of the '
                                                           'parking lot')
    full = serializers.SerializerMethodField(
        help_text='returns True if the lot is full else False')
    motorcycle_spots_available = serializers.SerializerMethodField(
        help_text='returns the number of motorcycle spots still available')
    car_spots_available = serializers.SerializerMethodField(
        help_text='returns the number of car spots still available')
    van_spots_available = serializers.SerializerMethodField(
        help_text='returns the number of van spots still available')
    spots_taken_by_vans = serializers.SerializerMethodField(
        help_text='returns the number of spots currently occupied by vans')

    def get_full(self, obj):
        return not ParkingSpace.objects.filter(lot=obj, vehicle=None).exists()

    def get_motorcycle_spots_available(self, obj):
        return ParkingSpace.objects.filter(
            lot=obj,
            type=SpaceTypes.MOTORCYCLE,
            vehicle=None
        ).count()

    def get_car_spots_available(self, obj):
        return ParkingSpace.objects.filter(
            lot=obj,
            type=SpaceTypes.CAR,
            vehicle=None
        ).count()

    def get_van_spots_available(self, obj):
        return ParkingSpace.objects.filter(
            lot=obj,
            type=SpaceTypes.VAN,
            vehicle=None
        ).count()

    def get_spots_taken_by_vans(self, obj):
        return ParkingSpace.objects.filter(
            lot=obj,
            vehicle__type=VehicleTypes.VAN
        ).count()


class ParkVehicleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=VehicleTypes.choices,
        help_text=' '.join([f'{vt.name}: {vt.value}' for vt in VehicleTypes]))
    lot_name = serializers.CharField(
        max_length=100, help_text='The name of the parking lot')
    license_plate = serializers.CharField(
        max_length=10, help_text='Vehicles license plate number')

    def validate(self, data):
        lot = generics.get_object_or_404(
            ParkingLot, name=data['lot_name']
        )
        vehicle_type = data['type']

        spots = []
        if vehicle_type == VehicleTypes.MOTORCYCLE:
            if spot := ParkingSpace.objects.filter(
                    lot=lot, vehicle=None, type=SpaceTypes.MOTORCYCLE
            ).order_by('number').first():
                spots.append(spot)
            elif spot := ParkingSpace.objects.filter(
                    lot=lot, vehicle=None, type=SpaceTypes.CAR
            ).order_by('number').first():
                spots.append(spot)
            elif spot := ParkingSpace.objects.filter(
                    lot=lot, vehicle=None, type=SpaceTypes.VAN
            ).order_by('number').first():
                spots.append(spot)
        elif vehicle_type == VehicleTypes.CAR:
            if spot := ParkingSpace.objects.filter(
                    lot=lot, vehicle=None, type=SpaceTypes.CAR
            ).order_by('number').first():
                spots.append(spot)
            elif spot := ParkingSpace.objects.filter(
                    lot=lot, vehicle=None, type=SpaceTypes.VAN
            ).order_by('number').first():
                spots.append(spot)
        elif vehicle_type == VehicleTypes.VAN:
            if spot := ParkingSpace.objects.filter(
                    lot=lot, vehicle=None, type=SpaceTypes.VAN
            ).order_by('number').first():
                spots.append(spot)
            elif spot := ParkingSpace.objects.filter(
                    lot=lot,
                    vehicle=None,
                    type=SpaceTypes.CAR,
                    previous__isnull=False,
                    next__isnull=False,
                    previous__vehicle=None,
                    next__vehicle=None,
            ).order_by('number').first():
                spots = [spot.previous, spot, spot.next]

        if not spots:
            raise ValidationError('Sorry no spots available for your vehicle')

        data['spots'] = spots
        data['lot'] = lot
        return data

    def save(self):
        vehicle = Vehicle.objects.create(
            type=self.validated_data['type'],
            license_plate=self.validated_data['license_plate']
        )
        for spot in self.validated_data['spots']:
            spot.vehicle = vehicle
            spot.save()

        return vehicle


class VehicleSerializer(serializers.Serializer):
    license_plate = serializers.CharField(
        max_length=10, help_text='Vehicles License plate number')
    minutes_parked = serializers.SerializerMethodField(
        help_text='returns how long the vehicle has been parked')

    def get_minutes_parked(self, obj):
        duration = datetime.now(pytz.UTC) - obj.parked_at
        return duration.total_seconds() // 60
