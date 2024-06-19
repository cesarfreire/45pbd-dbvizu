from django.http import HttpResponse
from django.urls import path
from . import views


def ping_load_balancer(request):
    return HttpResponse(status=200)


urlpatterns = [
    path('', views.home, name='home'),
    path('ping', ping_load_balancer),
    path('test_connection', views.test_connection, name='test_connection'),
]