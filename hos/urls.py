from django.urls import path
from . import views

urlpatterns = [
    
    path('hos/check', views.check, name='hos_check'),
    path('hos/demands/demand', views.hos_dealer_demand_check, name='hos_dealer_demand'), 

   
]

