from django.shortcuts import render
from django.http import HttpResponse
from datetime import date

from django.shortcuts import render
from django.conf.urls.static import static
import psycopg2 as ps
from .models import Ship
conn = ps.connect(dbname="seabattles", host="localhost", user="student", password="pass", port="5432")
cursor = conn.cursor()

'''
allItems = [
            {'name': "Авианосец Дзуйкаку",
             'src': '/static/zuikaku.jpg', 'id': 1,
             'desc': 'Зенитное вооружение корабля: 16 x 127-мм, бронирование: до 21,5 см',
             'params': [{'year': 'Год ввода в строй - 1941', 'displacement': 'Водоизмещение 30 000 т', 'length': 'Длина корпуса - 237 м', 'speed': 'Скорость хода 34 узла'}],
            },
            {'name': "Линкор Пенсильвания",
             'src': '/static/Pensilvania.jpg', 'id': 2,
             'desc': 'Вооружение корабля:  	4 × 3 — 356-мм и 22 × 1 — 127-мм, бронирование: 343 мм',
             'params': [{'year': 'Год ввода в строй - 1916', 'displacement': 'Водоизмещение 31 400 т', 'length': 'Длина корпуса - 185,4 м', 'speed': 'Скорость хода 21 узла'}]},
            {'name': "Тяжёлый крейсер Нати",
             'src': '/static/Nachi.jpg', 'id': 3,
             'desc': 'Вооружение корабля: 5 × 2 — 200-мм, бронирование: 102 мм',
             'params': [{'year': 'Год ввода в строй - 1928', 'displacement': 'Водоизмещение 15 933 т', 'length': 'Длина корпуса - 203,76 м', 'speed': 'Скорость хода 35,5 узла'}]},
        ]
'''

def shipList(request, sear = ""):
    return render(request, 'shipList.html', {'data': {
        'shipList': Ship.objects.filter(status = "действует").filter(name__icontains=sear).order_by('year'),
        'src' : sear
    }})

def search(request):
    '''try:
        searchQuery = request.GET['text']
    except:
        searchQuery = ''
    return shipList(request, searchQuery)'''
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


