from django.shortcuts import render
from django.http import HttpResponse
from datetime import date

from django.shortcuts import render
from django.conf.urls.static import static


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

draftItems = [1,2,3]

def shipList(request, sear = "", items = allItems, draftItems=draftItems):
    selItems = []
    if sear != "":
        for i in items:
            if sear in i['name']:
                selItems.append(i)
    else:
        selItems = items
    return render(request, 'shipList.html', {'data': {
        'shipList': selItems,
        'src': sear,
        'draft': len(draftItems)
    }})

def search(request):
    try:
        searchQuery = request.GET['text']
    except:
        searchQuery = ''
    return shipList(request, searchQuery)

def getShip(request, id, items = allItems):
    return render(request, 'ship.html', {'data':items[id-1]})

def getDraft(request, draftItems=draftItems, items = allItems):
    return render(request, 'draftCompaund.html', {'data':[i for i in items if (i['id'] in draftItems)]})