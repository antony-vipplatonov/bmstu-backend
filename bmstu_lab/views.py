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
from pathlib import Path
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
            Appl = get_object_or_404(Compaund, creatorname=get_creator(), status="черновик").id
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

class ShipDetail(APIView):
    model_class = Ship
    serializer_class = ShipSerializer
    def get(self, request, id, format=None):
        Ship = self.model_class.objects.filter(id=id)[0]
        serializer1 = self.serializer_class(Ship)
        return Response(serializer1.data)
    def delete(self, request, id, format=None):
        if str(id) + "/" in [obj.object_name for obj in client.list_objects(bucket_name="images")]:
            for obj in [obj.object_name for obj in client.list_objects(bucket_name="images", prefix=str(id) + "/")]:
                client.remove_object(bucket_name="images", object_name=obj)
        logging.debug(1)
        Ship = get_object_or_404(self.model_class, id=id)
        Ship.status = "удалён"
        Ship.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def post(self, request, id, format=None):
        src = request.data.get("src", 0)
        name = request.data.get("name", str(id))
        Ship = get_object_or_404(self.model_class, id=id)
        file = request.FILES['image']
        if src and Ship:
            if str(id)+"/" in [obj.object_name for obj in client.list_objects(bucket_name="images")]:
                for obj in [obj.object_name for obj in client.list_objects(bucket_name="images", prefix = str(id)+"/")]:
                    client.remove_object(bucket_name="images", object_name=obj)
            val = URLValidator()

            val(src)
            img = urlopen(src)
            img1 = urlopen(src)
            client.put_object(bucket_name='images',  # необходимо указать имя бакета,
                              object_name=str(id) + "/" + name + "." + src.split(".")[-1],
                              # имя для нового файла в хранилище
                              data=img,
                              length=len(img1.read())
                              )
            Ship.image_src = f"http://localhost:9000/images/{id}/{name}.{src.split('.')[-1]}"
            Ship.save()
            return Response(status=status.HTTP_201_CREATED)
        elif file and Ship:
            if str(id) + "/" in [obj.object_name for obj in client.list_objects(bucket_name="images")]:
                for obj in [obj.object_name for obj in client.list_objects(bucket_name="images", prefix=str(id) + "/")]:
                    client.remove_object(bucket_name="images", object_name=obj)
            client.put_object(bucket_name='images',  # необходимо указать имя бакета,
                              object_name=str(id) + "/" + name + Path(file.name).suffix,
                              # имя для нового файла в хранилище
                              data=file,
                              length=len(file)
                              )

            Ship.image_src = f"http://localhost:9000/images/{id}/{name}{Path(file.name).suffix}"
            Ship.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        """
        Обновляет информацию о голосовании (для модератора)
        """
        Ship = get_object_or_404(self.model_class, id=id)
        serializer = self.serializer_class(Ship, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

class CompaundList(APIView):
    model_class = Compaund
    serializer_class = CompaundSerializer
    def get(self, request, format=None):
        status = request.GET.get('status', "")
        dateFrom = request.GET.get('dateFrom', "0001-01-01")
        dateTo = request.GET.get('dateTo', "9999-12-01")
        if status:
            NOList = self.model_class.objects.filter(status=status).filter(dataform__date__gte=dateFrom).filter(dataform__date__lte=dateTo).order_by('dataform')
        else:
            NOList = self.model_class.objects.filter(dataform__date__gte=dateFrom).filter(dataform__date__lte=dateTo).order_by('dataform')
        serializer = self.serializer_class(NOList, many=True)
        for i in serializer.data:
            if i["creatorname"]:
                i["creatorname"] = list(Users.objects.values("id","name","email","phone").filter(id=i["creatorname"]))[0]
            if i["moderatorname"]:
                i["moderatorname"] = list(Users.objects.values("id", "name", "email", "phone").filter(id=i["moderatorname"]))[0]
        return Response(serializer.data)

class CompaundDetail(APIView):
    model_class = Compaund
    serializer_class = CompaundSerializer
    def get(self, request, id, format=None):
        try:
            Appl = self.model_class.objects.filter(id=id)[0]
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ApplComp = CompaundShips.objects.filter(idcompaund=id)
        Ships = Ship.objects.filter(id__in=[obj['idship'] for obj in list(ApplComp.values("idship"))])
        serializer1 = self.serializer_class(Appl)
        serializer2 = ShipSerializer(Ships, many=True)
        res = {"Application": serializer1.data, "Ships": serializer2.data}
        for ship in res["Ships"]:
            ship["captain"] = get_object_or_404(CompaundShips, idship=ship["id"], idcompaund=id).captain
        if res["Application"]["creatorname"]:
            res["Application"]["creatorname"] = list(Users.objects.values("id", "name", "email", "phone").filter(id=res["Application"]["creatorname"]))[0]
        if res["Application"]["moderatorname"]:
            res["Application"]["moderatorname"] = list(Users.objects.values("id", "name", "email", "phone").filter(id=res["Application"]["moderatorname"]))[0]
        return Response(res)
    def put(self, request, id, format=None):
        try:
            Appl = get_object_or_404(Compaund, id=id)
        except:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        admiralname = request.data.get("admiralname", 0)
        country = request.data.get("country", 0)
        victory = request.data.get("victory", 0)
        battledate = request.data.get("battledate", 0)
        if  Appl:
            if admiralname:
                logging.debug(admiralname)
                Appl.admiralname = admiralname
                Appl.save()
                ser = CompaundSerializer(Appl)
            if country:
                logging.debug(country)
                Appl.country = country
                Appl.save()
                ser = CompaundSerializer(Appl)
            if victory:
                logging.debug(victory)
                Appl.victory = victory
                Appl.save()
                ser = CompaundSerializer(Appl)
            if battledate:
                logging.debug(battledate)
                Appl.battledate = battledate
                Appl.save()
                ser = CompaundSerializer(Appl)
            return Response(ser.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['Put'])
def formAppl(request, format=None):
    try:
        Appl = get_object_or_404(Compaund, creatorname=get_creator(), status="черновик")
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    Appl.status = "сформирован"
    Appl.dataform = datetime.datetime.now()
    Appl.save()
    ser = CompaundSerializer(Appl)
    return Response(ser.data)

@api_view(['DELETE'])
def delAppl(request, format=None):
    try:
        Appl = get_object_or_404(Compaund, creatorname=get_creator(), status="черновик")
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    Appl.status = "удалён"
    Appl.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['Put'])
def chstatusAppl(request, id, format=None):
    try:
        Appl = get_object_or_404(Compaund, id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    stat = request.GET.get("status", 0)
    if list(Users.objects.filter(id=get_admin()).values())[0]['ismoderator'] is True and Appl.status == "сформирован" and stat:
        Appl.status = stat
        logging.debug(Appl)
        Appl.moderatorname_id = get_admin()
        Appl.dataend = datetime.datetime.now()
        Appl.save()
        ser = CompaundSerializer(Appl)
        return Response(ser.data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
@api_view(['POST'])
def addToAppl(request, id, format=None):
    captain = request.data.get("captain", 0)
    try:
        Appl = get_object_or_404(Compaund, creatorname=get_creator(), status="черновик")
        logging.debug(Appl)
    except:
        serializer = CompaundSerializer(data={"creatorname": get_creator()})
        logging.debug(serializer.is_valid())
        if serializer.is_valid():

            serializer.save()
        logging.debug(serializer.errors)
        Appl = get_object_or_404(Compaund, creatorname=get_creator(), status="черновик")
        logging.debug(Appl)
    ser = CompaundShipsSerializer(data={"idcompaund": Appl.id, "idship": id, "captain": captain})
    if ser.is_valid():
        logging.debug(ser.validated_data)
        ser.save()
    else:
        logging.debug(ser.errors)
    return Response(ser.data)

class MM(APIView):
    def delete(self, request, idAppl, idServ, format=None):
        try:
            applserv = get_object_or_404(CompaundShips, idship=idServ, idcompaund=idAppl)
            applserv.delete()
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, idAppl, idServ, format=None):
        try:
            applserv = get_object_or_404(CompaundShips, idship=idServ, idcompaund=idAppl)
        except:
           return Response(status=status.HTTP_404_NOT_FOUND)
        captain = request.data.get("captain", 0)
        if captain:
            applserv.captain = captain
            applserv.save()
            ser = CompaundShipsSerializer(applserv)
            return Response(ser.data)
        Response(status=status.HTTP_400_BAD_REQUEST)