from decimal import Decimal
import psycopg2
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny

from bmstu_lab.models import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from bmstu_lab.serializers import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes
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
import redis
import uuid
from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .permission import IsManager

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

session_storage = redis.StrictRedis(host=settings.REDIS_HOST,
                                    port=settings.REDIS_PORT)
def check_session(request):
    ssid = request.COOKIES.get("session_id", -1)
    username = session_storage.get(ssid)
    if not username:
        return -1
    else:
        return get_object_or_404(Users, username=username.decode('utf-8'))

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

class ShipList(APIView):
    model_class = Ship
    serializer_class = ShipSerializer

    def get(self, request, format=None):
        ssid = request.COOKIES.get("session_id", -1)
        username = session_storage.get(ssid)
        if not username:
            sear = request.GET.get('text', "")
            NOList = self.model_class.objects.filter(status="действует").filter(name__icontains=sear).order_by('name')
            serializer = self.serializer_class(NOList, many=True)
            for i in serializer.data:
                try:
                    i["image_src"] = i["image_src"].replace("127.0.0.1",
                                                            "192.168.43.230")  # socket.gethostbyname(socket.gethostname()))
                    i["image_src"] = i["image_src"].replace("localhost",
                                                            "192.168.43.230")  # socket.gethostbyname(socket.gethostname()))
                except:
                    pass
            return Response({"ships": serializer.data})
        else:
            user = get_object_or_404(Users, username=username.decode('utf-8'))
        try:
            Appl = get_object_or_404(Compaund, creatorname=user.id, status="черновик").id
        except:
            Appl = None
        sear = request.GET.get('text', "")
        NOList = self.model_class.objects.filter(status = "действует").filter(name__icontains=sear).order_by('name')
        serializer = self.serializer_class(NOList, many=True)
        for i in serializer.data:
            try:
                i["image_src"] = i["image_src"].replace("127.0.0.1",
                                                        "192.168.43.230")  # socket.gethostbyname(socket.gethostname()))
                i["image_src"] = i["image_src"].replace("localhost",
                                                        "192.168.43.230")  # socket.gethostbyname(socket.gethostname()))
            except:
                pass
        return Response({"ships":serializer.data, "draftID": Appl})

    @swagger_auto_schema(request_body=ShipSerializer)
    @csrf_exempt
    def post(self, request, format=None):
        user = check_session(request)
        if user == -1 or user.is_staff == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
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
        i = serializer1.data
        try:
            i["image_src"] = i["image_src"].replace("127.0.0.1",
                                                    "192.168.43.230")  # socket.gethostbyname(socket.gethostname()))
            i["image_src"] = i["image_src"].replace("localhost",
                                                    "192.168.43.230")  # socket.gethostbyname(socket.gethostname()))
        except:
            pass
        return Response(i)

    @csrf_exempt
    def delete(self, request, id, format=None):
        user = check_session(request)
        if user == -1 or user.is_staff == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if str(id) + "/" in [obj.object_name for obj in client.list_objects(bucket_name="images")]:
            for obj in [obj.object_name for obj in client.list_objects(bucket_name="images", prefix=str(id) + "/")]:
                client.remove_object(bucket_name="images", object_name=obj)
        logging.debug(1)
        Ship = get_object_or_404(self.model_class, id=id)
        Ship.status = "удалён"
        Ship.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @csrf_exempt
    @swagger_auto_schema(request_body=ShipSerializer)
    def put(self, request, id, format=None):
        user = check_session(request)
        if user == -1 or user.is_staff == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
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
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        user = check_session(request)
        if user == -1:
            return Response(status=status.HTTP_403_FORBIDDEN)
        stat = request.GET.get('status', "")
        dateFrom = request.GET.get('dateFrom', "0001-01-01")
        dateTo = request.GET.get('dateTo', "9999-12-01")
        if user.is_staff:
            if stat:
                NOList = self.model_class.objects.filter(status=stat).filter(dataform__date__gte=dateFrom).filter(dataform__date__lte=dateTo).order_by('dataform')
            else:
                NOList = self.model_class.objects.filter(dataform__date__gte=dateFrom).filter(dataform__date__lte=dateTo).order_by('dataform')
            serializer = self.serializer_class(NOList, many=True)
            for i in serializer.data:
                if i["creatorname"]:
                    i["creatorname"] = list(Users.objects.values("id","username","email","phone").filter(id=i["creatorname"]))[0]
                if i["moderatorname"]:
                    i["moderatorname"] = list(Users.objects.values("id", "username", "email", "phone").filter(id=i["moderatorname"]))[0]
        else:
            if stat:
                NOList = self.model_class.objects.filter(status=stat).filter(dataform__date__gte=dateFrom).filter(dataform__date__lte=dateTo).filter(creatorname=user.id).order_by('dataform')
            else:
                NOList = self.model_class.objects.filter(dataform__date__gte=dateFrom).filter(dataform__date__lte=dateTo).filter(creatorname=user.id).order_by('dataform')
            serializer = self.serializer_class(NOList, many=True)
            for i in serializer.data:
                if i["creatorname"]:
                    i["creatorname"] = list(Users.objects.values("id","username","email","phone").filter(id=i["creatorname"]))[0]["username"]
                if i["moderatorname"]:
                    i["moderatorname"] = list(Users.objects.values("id", "username", "email", "phone").filter(id=i["moderatorname"]))[0]["username"]
        return Response(serializer.data)

class CompaundDetail(APIView):
    model_class = Compaund
    serializer_class = CompaundSerializer
    def get(self, request, id, format=None):
        user = check_session(request)
        if user == -1:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if user.is_staff:
            try:
                Appl = self.model_class.objects.filter(id=id)[0]
            except IndexError:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                Appl = self.model_class.objects.filter(id=id).filter(creator__id=user.id)[0]
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
            list(Users.objects.values("id", "username", "email", "phone").filter(id=res["Application"]["creatorname"]))[0][
                "username"]
        if res["Application"]["moderatorname"]:
            res["Application"]["moderatorname"] = list(Users.objects.values("id", "name", "email", "phone").filter(id=res["Application"]["moderatorname"]))[0]
            list(Users.objects.values("id", "username", "email", "phone").filter(id=res["Application"]["moderatorname"]))[0][
            "username"]
        return Response(res)

    @csrf_exempt
    def put(self, request, id, format=None):
        user = check_session(request)
        if user == -1:
            return Response(status=status.HTTP_403_FORBIDDEN)
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

@csrf_exempt
@api_view(['Put'])
def addImg(request, id, format=None):
    src = request.data.get("src", 0)
    name = request.data.get("name", str(id))
    ship = get_object_or_404(Ship, id=id)
    file = request.FILES['image']
    if src and ship:
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
        ship.image_src = f"http://localhost:9000/images/{id}/{name}.{src.split('.')[-1]}"
        ship.save()
        return Response(status=status.HTTP_201_CREATED)
    elif file and ship:
        if str(id) + "/" in [obj.object_name for obj in client.list_objects(bucket_name="images")]:
            for obj in [obj.object_name for obj in client.list_objects(bucket_name="images", prefix=str(id) + "/")]:
                client.remove_object(bucket_name="images", object_name=obj)
        client.put_object(bucket_name='images',  # необходимо указать имя бакета,
                          object_name=str(id) + "/" + name + Path(file.name).suffix,
                          # имя для нового файла в хранилище
                          data=file,
                          length=len(file)
                          )

        ship.image_src = f"http://localhost:9000/images/{id}/{name}{Path(file.name).suffix}"
        ship.save()
        return Response(status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['Put'])
def formAppl(request, format=None):
    user = check_session(request)
    if user == -1:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        Appl = get_object_or_404(Compaund, creatorname=user.id, status="черновик")
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    Appl.status = "сформирован"
    Appl.dataform = datetime.datetime.now()
    Appl.save()
    ser = CompaundSerializer(Appl)
    return Response(ser.data)

@csrf_exempt
@api_view(['DELETE'])
def delAppl(request, format=None):
    user = check_session(request)
    if user == -1:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        Appl = get_object_or_404(Compaund, creatorname=user.id, status="черновик")
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    Appl.status = "удалён"
    Appl.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
@swagger_auto_schema(method='Put', request_body=CompaundSerializer)
@api_view(['Put'])
def chstatusAppl(request, id, format=None):
    user = check_session(request)
    if user == -1 or user.is_staff == False:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        Appl = get_object_or_404(Compaund, id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    stat = request.GET.get("status", 0)
    if Appl.status == "сформирован" and stat in ["отменён", "завершён"]:
        Appl.status = stat
        Appl.moderatorname_id = user.id
        Appl.dataend = datetime.datetime.now()
        Appl.save()
        ser = CompaundSerializer(Appl)
        return Response(ser.data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
@csrf_exempt
@api_view(['POST'])
def addToAppl(request, id, format=None):
    user = check_session(request)
    if user == -1:
        return Response(status=status.HTTP_403_FORBIDDEN)
    captain = request.data.get("captain", 0)
    try:
        Appl = get_object_or_404(Compaund, creatorname=user.id, status="черновик")
        logging.debug(Appl)
    except:
        serializer = CompaundSerializer(data={"creatorname": user.id})
        logging.debug(serializer.is_valid())
        if serializer.is_valid():

            serializer.save()
        Appl = get_object_or_404(Compaund, creatorname=user.id, status="черновик")
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


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object = serializer.save()
            self.object.set_password(self.object.password)
            self.object.save()
            headers = self.get_success_headers(serializer.data)
            return Response({'status': 'ok', **serializer.data}, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response({'status': 'error', "error":serializer.errors})
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]


@csrf_exempt
@swagger_auto_schema(method='post', request_body=UsersSerializer)
@authentication_classes([])
@api_view(['Post'])
def login_view(request):
    username = request.data.get("username") # допустим передали username и password
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        #login(request, user)
        random_key = uuid.uuid4()
        session_storage.set(str(random_key), username)

        response = Response({'status': 'ok'})
        response.set_cookie("session_id", random_key)
        return response
    else:
        return Response({'status': 'error', 'error': 'login failed'})

@api_view(('GET',))
def logout_view(request):
    user = check_session(request)
    if user == -1:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        Appl = get_object_or_404(Compaund, creatorname=user.id, status="черновик")
        Appl.delete()
    except:
        pass
    ssid = request.COOKIES.get("session_id", -1)
    session_storage.delete(ssid)
    response = Response({'status': 'Success'})
    response.delete_cookie("session_id")

    #logout(request)
    return response
@api_view(('GET',))
def userInfo(request):
    user = check_session(request)
    if user == -1:
        return Response(status=status.HTTP_403_FORBIDDEN)
    return Response(UsersSerializer(user).data)
