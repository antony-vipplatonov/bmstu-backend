from decimal import Decimal
import psycopg2
from bmstu_lab.models import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from bmstu_lab.serializers import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from minio import Minio
import logging
from django.conf import settings
from urllib.request import urlopen
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import os

fmt = getattr(settings, 'LOG_FORMAT', None)
lvl = getattr(settings, 'LOG_LEVEL', logging.DEBUG)

logging.basicConfig(format=fmt, level=lvl)
logging.debug("Logging started on %s for %s" % (logging.root.name, logging.getLevelName(lvl)))

client = Minio(endpoint="localhost:9000",   # адрес сервера
               access_key='minioadmin',          # логин админа
               secret_key='minioadmin',       # пароль админа
               secure=False)                # опциональный параметр, отвечающий за вкл/выкл защищенное TLS соединение

import psycopg2 as ps
from .models import Ship
conn = ps.connect(dbname="seabattles", host="localhost", user="student", password="pass", port="5432")
cursor = conn.cursor()

def get_creator():
    return 1
def get_admin():
    return 2

class ShipList(APIView):
    model_class = Ship
    serializer_class = ShipSerializer

    def get(self, request, format=None):
        try:
            Appl = get_object_or_404(Compaund, creator=get_creator(), status="черновик").id
        except:
            Appl = None
        sear = request.GET.get('text', "")
        NOList = self.model_class.objects.filter(status = "действует").filter(name__icontains=sear).order_by('name')
        serializer = self.serializer_class(NOList, many=True)
        return Response({"ships":serializer.data, "draftID": Appl})
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
