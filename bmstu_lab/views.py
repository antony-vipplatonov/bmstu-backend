from django.shortcuts import render
from django.http import HttpResponse
from datetime import date

from django.shortcuts import render
from django.conf.urls.static import static


allItems = [
            {'name': "Авианосец Дзуйкаку",
             'src': '/static/zuikaku.jpg', 'id': 1,
             'desc': 'Спущен на воду в 1939',
             'params': [{'displacement': 'Водоизмещение 30 000 т', 'speed': 'Скорость хода 34 узла'}],
            },
            {'name': "Линкор Пенсильвания",
             'src': '/static/Pensilvania.jpg', 'id': 2,
             'desc': 'Спущен на воду в 1915',
             'params': [{'displacement': 'Водоизмещение 31 400 т', 'speed': 'Скорость хода 21 узла'}]},
            {'name': "Тяжёлый крейсер Нати",
             'src': '/static/Nachi.jpg', 'id': 3,
             'desc': 'Спущен на воду в 1927',
             'params': [{'displacement': 'Водоизмещение 15 933 т', 'speed': 'Скорость хода 35,5 узла'}]},
        ]

def shipList(request, sear = "", items = allItems):
    selItems = []
    if sear != "":
        for i in items:
            if sear in i['name']:
                selItems.append(i)
    else:
        selItems = items
    return render(request, 'shipList.html', {'data': {
        'shipList': selItems,
        'src': sear
    }})

def search(request):
    '''if request != "http://127.0.0.1:8000/seabattles/":
        searchQuery = request.GET['text']
    else:
        searchQuery = '''
    searchQuery = request.GET['text']
    return shipList(request, searchQuery)

def getShip(request, id, items = allItems):
    return render(request, 'ship.html', {'data':items[id-1]})