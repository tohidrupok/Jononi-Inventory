from django.urls import path
from . import views

urlpatterns = [
    path('base/', views.base, name='base'),
    path('index/', views.index, name='dashboard-index'),
    path('warehouse/index/', views.warehouse, name='warehouse-index'),
     path('get-product-tp/<int:product_id>/', views.get_product_tp, name='get_product_tp'),
    
    path('add-shope/', views.shops, name='add-shope'), 
    path('edit-shop/<int:shop_id>/', views.edit_shop, name='edit-shop'),
    path('delete-shop/<int:shop_id>/', views.delete_shop, name='delete-shop'),
    
    path('daily-report/', views.daily_report, name='daily_report'),
    path('sr-order/', views.dealer_orders_view, name='sr-order'),
    path('order/<int:pk>/note/', views.order_note, name='note'), 
    path('order/<int:pk>/cost/', views.order_cost, name='cost'), 
    
    path('get-districts/', views.get_districts, name='get-districts'),
    path('get-thanas/', views.get_thanas, name='get-thanas'),
    path('get-areas/', views.get_areas, name='get-areas'), 


    path('demand/', views.demand , name ='demand'),
    path('demand/check/', views.demand_request_check, name='demand_check'),

    path('offer/active/', views.active_offer_list, name='active_offer_list'), 
    path('order/manage/', views.order_manage , name='order_manage'), 
    path('order/<int:pk>/edit/', views.edit_order, name='edit_order'),
    path('order/<int:pk>/delete/', views.delete_order, name='delete_order'),

    path('reached/<int:need_id>/', views.reached_product, name='reached_product'),


    path('dealear/stocks/', views.user_stocks, name='user_stocks'),
    path('demand/<int:pk>/edit/', views.edit_demand, name='edit_demand'),
    path('demand/<int:pk>/delete/', views.delete_demand, name='delete_demand'),
    
    path('demand/<int:pk>/paid/', views.demand_paid, name='paid'), 
    path('demand/<int:pk>/payment/', views.demand_payment, name='Due-Payment'), 
    path('demand/<int:pk>/cost/', views.demand_cost, name='demand-cost'),
    
    
    path('order/summary/', views.order_summary, name='order_summary'),
    path('confirm/<int:need_id>/', views.confirm_product, name='confirm_product'),
    
    
    path('generate-pdf/<int:order_id>/', views.generate_pdf, name='generate_pdf'),
    
    path('demand/payment-commission/', views.payment_commission, name='payment-commission'),
    
    
    
    
]
