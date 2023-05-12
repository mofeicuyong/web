from django.shortcuts import render
from django.http import HttpResponse, Http404
import json
from bson import json_util
from .models import *
from django.core import serializers
import datetime
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import random
import string
from django.db.models import Sum
import requests


def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def stamp_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def findflight(request, format=None):
    if request.method == "GET":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # test if the departue airport appears in the database

        dep_date = body['dep_date']
        dep_airport = body['dep_airport']

        dest_airport = body['dest_airport']

        try:
            datetime_object = datetime.datetime.strptime(dep_date, '%Y-%m-%d')
        except:
            return HttpResponse("Sorry. %s does no comply to our format standards." % (body['dep_date']),
                                content_type="text/plain", status=503)

        all_entries = Flights.objects.filter(dep_airport=dep_airport,
                                             des_airport=dest_airport,

                                             )

        flight_results = []
        for entry in all_entries:
            flight_result = {'flight_id': str(entry.pk), 'flight_num': entry.plane_number,
                             'dep_airport': entry.dep_airport, 'dest_airport': entry.des_airport,
                             'dep_datetime': str(entry.dep_datetime), 'arr_datetime': str(entry.arrival_datetime),
                             'seatbusi_occupied': entry.seatbusi_occupied, 'max_seatbusi': entry.max_seatbusi,
                             'seatbusi_price': entry.seatbusi_price, 'seatcoom_occupied': entry.seatcoom_occupied,
                             'max_seatcoom': entry.max_seatcoom, 'seatcoom_price': entry.seatcoom_price,
                             'seatfirst_occupied': entry.seatfirst_occupied, 'max_seatfirst': entry.max_seatfirst,
                             'seatfirst_price': entry.seatfirst_price}

            flight_results.append(flight_result)

        findflight = {}
        findflight['flights'] = flight_results

        if all_entries:
            return HttpResponse(json.dumps(findflight), content_type="application/json")
        else:
            return HttpResponse("Service Unavailable", content_type="text/plain", status=503)


@csrf_exempt
def bookflight(request):
    global seats_booked, num_of_passengers_allowed
    if request.method == "POST" or "GET":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        final_list = []

        booking_num = random_generator()

        flight_object = Flights.objects.get(flight_id=body['flight_number'])

        level1 = body['passengers'][0]
        level = level1['seat_type']

        # find the bookings already made
        if (level == 'business'):
            seats_booked = flight_object.seatbusi_occupied
            num_of_passengers_allowed = flight_object.max_seatbusi
        if (level == 'coom'):
            seats_booked = flight_object.seatbusi_occupied
            num_of_passengers_allowed = flight_object.max_seatcoom
        if (level == 'first'):
            seats_booked = flight_object.seatbusi_occupied
            num_of_passengers_allowed = flight_object.max_seatfirst
        # should check if a booking can be made

        if (seats_booked + len(body['passengers']) <= num_of_passengers_allowed):

            Booking.objects.create(
                flight_id=flight_object,
                booking_id=booking_num
            )
            booking_object = Booking.objects.get(booking_id=booking_num)
            for result in body['passengers']:

                name = result['passenger_name']
                passenger_id = result['passenger_id']
                level = result['seat_type']
                phone = result['passenger_phone']
                customer = Customer.objects.create(booking_id=booking_object, name=name, seat_type=level, phone=phone,
                                        customer_id=passenger_id)
                customer.save()

            payload = {}
            payload['booking_id'] = booking_num



        else:
            return HttpResponse("WE ARE FULL BOOKED SORRY!", content_type="text/plain")

        if payload:
            return HttpResponse(json.dumps(payload), content_type="application/json", status=201)
        else:
            return HttpResponse("Something went wrong ", content_type="text/plain")


@csrf_exempt
def payforbooking(request):
    if request.method == "POST" or "GET":

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        session = requests.session()

        try:
            booking_object = Booking.objects.get(booking_id=body["booking_id"])
        except:
            return HttpResponse(
                "Sorry. The BOOKING NUMBER %s is not not storred in our database." % (body['booking_num']),
                content_type="text/plain", status=503)

        all_entries = Customer.objects.filter(booking_id=booking_object.booking_id)

        payload = {}
        payload['MerchantOrderId'] = booking_object.booking_id
        booking_object = Booking.objects.get(booking_id=booking_object.booking_id)
        level = Customer.objects.get(booking_id=booking_object.booking_id).seat_type

        if (level == 'business'):
            payload['price'] = Flights.objects.get(flight_id=booking_object.flight_id.flight_id).seatbusi_price * len(all_entries)
        if (level == 'coom'):
            payload['price'] = Flights.objects.get(flight_id=booking_object.flight_id.flight_id).seatcoom_price * len(all_entries)
        if level == 'first':

           payload['price'] = Flights.objects.get(flight_id=booking_object.flight_id.flight_id).seatfirst_price * len(all_entries)

        r = session.post("http://127.0.0.1:8000/paymentservice/order/", headers={'content-type': "application/json"}, data=json.dumps(payload))

        createinvoice_payload = json.loads(r.text)
        #createinvoice_payload  = {'payment_id':114514,
        #                          'stamp':'winwin'}
        try:

            booking_object.stamp = createinvoice_payload['stamp']

            booking_object.payment_id = createinvoice_payload['payment_id']
            booking_object.save()

        except:
            print("Invoice not created")
        pay = {}
        pay["payment_id"] = createinvoice_payload['payment_id']

        return HttpResponse(json.dumps(pay), content_type="application/json")


@csrf_exempt
def confirm(request):
    global body
    if request.method == "POST" or "GET":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

    try:
        body['stamp'] = Booking.objects.get(booking_id=body['booking_id'])
        return HttpResponse('success', content_type="application/json", status=200)
    except:
        return HttpResponse('fail to pay', content_type="application/json", status=400)





@csrf_exempt
def cancelbooking(request):
    if request.method == "POST"or"GET":

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        session = requests.session()
        try:
            booking_object = Booking.objects.get(booking_id=body["booking_id"])
        except:
            return HttpResponse(
                "Sorry. There is no BOOKING for the following BOOKING NUMBER: %s" % (body['booking_num']), status=503)
        payload = {}
        all_entries = Customer.objects.filter(booking_id=booking_object.booking_id)
        booking_object = Booking.objects.get(booking_id=booking_object.booking_id)
        level1 = body['passengers'][0]

        level = Customer.objects.get(customer_id=level1['passenger_id'],booking_id=booking_object.booking_id).seat_type

        if level == 'business':
            payload['price'] = Flights.objects.get(flight_id=booking_object.flight_id.flight_id).seatbusi_price * len(
                all_entries)
        if (level == 'coom'):
            payload['price'] = Flights.objects.get(flight_id=booking_object.flight_id.flight_id).seatcoom_price * len(
                all_entries)
        if (level == 'first'):
            payload['price'] = Flights.objects.get(flight_id=booking_object.flight_id.flight_id).seatfirst_price * len(
                all_entries)
        payload["payment_id"] = booking_object.payment_id

        r = session.post("url = ' http://127.0.0.1:8000/paymentservice/refund/'", headers={'content-type': "application/json"}, data=json.dumps(payload))
        re = json.loads(r.text)
        #re = 200

        if re == 200:
            return HttpResponse("success",status=200)

        else:
            return HttpResponse("Service Unavailable", status=503)
