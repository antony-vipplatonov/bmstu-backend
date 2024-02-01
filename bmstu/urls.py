from django.contrib import admin
from django.urls import path
from bmstu_lab import views
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path(r'', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
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
    path('login',  views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('user/me', views.userInfo),
]
