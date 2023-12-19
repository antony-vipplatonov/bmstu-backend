from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('seabattles/', views.ShipList.as_view()),
    path('seabattles/<int:id>/', views.ShipDetail.as_view()),
    path('applications/', views.CompaundList.as_view()),
    path('applications/<int:id>/', views.CompaundDetail.as_view()),
    path('applications/form/', views.formAppl),
    path('applications/delete/', views.delAppl),
    path('applications/<int:id>/chstatus/', views.chstatusAppl),
    path('seabattles/<int:id>/addToAppl/', views.addToAppl),
    path('applications/<int:idAppl>/<int:idServ>/', views.MM.as_view()),
]
