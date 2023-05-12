from django.db import models
from django.utils import timezone
from django.db import models

class Flights(models.Model):
    flight_id = models.IntegerField(primary_key=True, default="unspecified")
    plane_number = models.CharField(max_length=50)
    dep_airport = models.CharField(max_length=100)
    des_airport = models.CharField(max_length=100)
    dep_datetime = models.DateTimeField(default=timezone.now)
    arrival_datetime = models.DateTimeField(default=timezone.now)
    seatbusi_occupied = models.IntegerField()
    max_seatbusi = models.IntegerField()
    seatbusi_price = models.FloatField()
    seatcoom_occupied = models.IntegerField()
    max_seatcoom = models.IntegerField()
    seatcoom_price = models.FloatField()
    seatfirst_occupied = models.IntegerField()
    max_seatfirst = models.IntegerField()
    seatfirst_price = models.FloatField()

class Refund(models.Model):
    refund_id = models.IntegerField(primary_key=True, default="unspecified")
    flight_id = models.ForeignKey('Booking', on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=50)
    refund_time = models.DateTimeField()

class Booking(models.Model):
    booking_id = models.CharField(max_length=50,primary_key=True, unique=True)
    payment_id = models.IntegerField(null=True)
    stamp = models.CharField(max_length=50)
    flight_id = models.ForeignKey(Flights, on_delete=models.CASCADE)

class Customer(models.Model):

    booking_id = models.ForeignKey(Booking, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=50,default="unspecified")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    seat_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
