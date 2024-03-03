from django.shortcuts import render
from django.http import HttpResponse
from datetime import date

from django.shortcuts import render
from django.conf.urls.static import static
import psycopg2 as ps
from .models import *
conn = ps.connect(dbname="seabattles", host="localhost", user="student", password="pass", port="5432")
cursor = conn.cursor()

draftItems = [1,2,3]

def shipList(request, sear = ""):
    return render(request, 'shipList.html', {'data': {'shipList': Ship.objects.filter(status = "действует").filter(name__icontains=sear).order_by('year'),
        'src' : sear,
        'draftCompaund': len(Ship.objects.filter(id__in = [i['idship_id'] for i in CompaundShips.objects.filter(idcompaund = 56).values()]).order_by('year'))
        }
    })


def search(request):
    delId = request.POST.get("del", -1)
    searchQuery = ''
    if delId == -1:
        searchQuery = request.GET.get('text', "")
    else:
        cursor.execute(f"update public.\"Ship\" set status = 'удалён'  where \"id\" = {delId}")
        conn.commit()

    return shipList(request, searchQuery)

def getShip(request, id):
    return render(request, 'ship.html', {'data':Ship.objects.filter(id = id)[0]})

def getDraft(request):
    return render(request, 'draftCompaund.html', {'data':Ship.objects.filter(id__in = [i['idship_id'] for i in CompaundShips.objects.filter(idcompaund = 56).values()]).order_by('year')})

