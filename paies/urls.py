from django.urls import path
from . import views

app_name = 'paies'

urlpatterns = [
    path('create_order', views.create_order, name='create_order'),
    path('check/<int:TimeStamp>', views.check_order, name='check_order'),
    path('newebpays_return', views.newebpay_return, name='newebpay_return'),
]
