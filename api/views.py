from django.utils.decorators import method_decorator

from drf_yasg.utils import swagger_auto_schema

from .models import ParkingLot, Vehicle
from .serializers import (
    ParkingLotQuerySerializer,
    ParkingLotSerializer,
    ParkingLotStatusSerializer,
    ParkVehicleSerializer,
    VehicleSerializer,
)

from rest_framework import generics


class CreateParkingLot(generics.CreateAPIView):
    serializer_class = ParkingLotSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=ParkingLotQuerySerializer,
    operation_description="""Returns the status of a parking lot."""))
class ParkingLotStatus(generics.RetrieveAPIView):
    serializer_class = ParkingLotStatusSerializer
    queryset = ParkingLot.objects.all()
    lookup_field = 'name'

    def get_object(self):
        serializer = ParkingLotQuerySerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        lot = generics.get_object_or_404(
            ParkingLot, name=serializer.validated_data['name'])
        return lot


class ParkVehicle(generics.CreateAPIView):
    serializer_class = ParkVehicleSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=VehicleSerializer,
    operation_description="""Returns the parking status of a vehicle."""))
class VehicleStatus(generics.RetrieveAPIView):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()
    lookup_field = 'license_plate'

    def get_object(self):
        serializer = VehicleSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return generics.get_object_or_404(
            Vehicle, license_plate=serializer.validated_data['license_plate'])


@method_decorator(name='delete', decorator=swagger_auto_schema(
    query_serializer=VehicleSerializer,
    operation_description="""Removes a vehicle from the parking lot."""))
class VehicleExit(generics.DestroyAPIView):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()
    lookup_field = 'license_plate'

    def get_object(self):
        serializer = VehicleSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return generics.get_object_or_404(
            Vehicle, license_plate=serializer.validated_data['license_plate'])
