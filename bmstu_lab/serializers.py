from bmstu_lab.models import *
from rest_framework import serializers


class CompaundSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Compaund
        # Поля, которые мы сериализуем
        fields = ["id", "name", "admiralname", "country", "victory", "status", "creatorname", "moderatorname", "datacreate", "dataform", "dataend", "battledate"]

class CompaundShipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompaundShips
        fields = ["id", "idship", "idcompaund", "captain"]

class ShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ship
        fields = ["id", "name", "weapon", "armoring", "year", "displacement", "length", "speed", "status", "image_src"]


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "phone", "password", "is_staff"]