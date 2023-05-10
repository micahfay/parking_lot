from rest_framework.test import APIRequestFactory, APITestCase
from django.urls import reverse

from .models import ParkingLot, ParkingSpace, Vehicle, SpaceTypes, VehicleTypes


class TestParkingLotCreation(APITestCase):
    def test_create_parking_lot(self):
        response = self.client.post(
            reverse('api:create_lot'),
            {'name': 'test lot', 'spaces':[1,1,1,2,2,2,3,3,3]},
            format='json')
        self.assertEqual(response.status_code, 201)
        assert ParkingLot.objects.get(name='test lot')
        assert ParkingSpace.objects.count() == 9


class TestVehiclePark(APITestCase):
    def setUp(self):
        response = self.client.post(
            reverse('api:create_lot'),
            {'name': 'test lot', 'spaces': [1, 1, 1, 2, 2, 2, 3, 3, 3]},
            format='json')
        self.assertEqual(response.status_code, 201)
        self.lot = ParkingLot.objects.get(name='test lot')
        assert ParkingSpace.objects.count() == 9

    def test_park_unpark_motorcycle(self):
        response = self.client.post(
            reverse('api:park_vehicle'),
            {'type': 1, 'license_plate': '123456', 'lot_name': self.lot.name},
            format='json')
        self.assertEqual(response.status_code, 201)
        assert Vehicle.objects.get(license_plate='123456')
        assert ParkingSpace.objects.get(
            number=0).vehicle.license_plate == '123456'

        response = self.client.delete(
            reverse('api:vehicle_exit') + '?license_plate=123456')
        self.assertEqual(response.status_code, 204)
        assert not Vehicle.objects.filter(license_plate='123456').exists()
        assert not ParkingSpace.objects.get(number=0).vehicle

    def test_park_unpark_car(self):
        response = self.client.post(
            reverse('api:park_vehicle'),
            {'type': 2, 'license_plate': '123456', 'lot_name': self.lot.name},
            format='json')
        self.assertEqual(response.status_code, 201)
        assert Vehicle.objects.get(license_plate='123456')
        assert ParkingSpace.objects.get(
            number=3).vehicle.license_plate == '123456'

        response = self.client.delete(
            reverse('api:vehicle_exit') + '?license_plate=123456')
        self.assertEqual(response.status_code, 204)
        assert not Vehicle.objects.filter(license_plate='123456').exists()
        assert not ParkingSpace.objects.get(number=3).vehicle

    def test_park_unpark_van(self):
        response = self.client.post(
            reverse('api:park_vehicle'),
            {'type': 3, 'license_plate': '123456', 'lot_name': self.lot.name},
            format='json')
        self.assertEqual(response.status_code, 201)
        assert Vehicle.objects.get(license_plate='123456')
        assert ParkingSpace.objects.get(
            number=6).vehicle.license_plate == '123456'

        response = self.client.delete(
            reverse('api:vehicle_exit') + '?license_plate=123456')
        self.assertEqual(response.status_code, 204)
        assert not Vehicle.objects.filter(license_plate='123456').exists()
        assert not ParkingSpace.objects.get(number=6).vehicle

    def test_park_unpark_van_in_three_car_spaces(self):
        ParkingSpace.objects.filter(type=SpaceTypes.VAN).delete()
        response = self.client.post(
            reverse('api:park_vehicle'),
            {'type': 3, 'license_plate': '123456', 'lot_name': self.lot.name},
            format='json')
        self.assertEqual(response.status_code, 201)
        assert Vehicle.objects.get(license_plate='123456')
        assert ParkingSpace.objects.filter(
            vehicle__type=VehicleTypes.VAN).count() == 3

        response = self.client.delete(
            reverse('api:vehicle_exit') + '?license_plate=123456')
        self.assertEqual(response.status_code, 204)
        assert not Vehicle.objects.filter(license_plate='123456').exists()
        assert not ParkingSpace.objects.filter(
            vehicle__type=VehicleTypes.VAN).exists()
