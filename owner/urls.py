from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('customers/', views.customers, name='dashboard-customers'),
    path('customers/detial/<int:pk>/', views.customer_detail,
         name='dashboard-customer-detail'),
    path('orders/', views.order, name='dashboard-order'), 

    path('products/', views.products, name='dashboard-products'),
    path('products/delete/<int:pk>/', views.product_delete,
         name='dashboard-products-delete'),
    path('products/edit/<int:pk>/', views.product_edit,
         name='dashboard-products-edit'),

    path('order/', views.final_order_list, name='order'),
    path('demands/', views.dealers_demand, name='dealers_demand'), 
    path('warehouse/demand/<int:pk>/edit/', views.admin_edit_demand, name='admin_edit_demand'),

    path('offer/', views.offer_list, name='offer_list'),
    path('offer/create/', views.offer_create, name='offer_create'),
    path('offer/<int:offer_id>/update/', views.offer_update, name='offer_update'),
    path('offer/<int:offer_id>/end/', views.offer_end, name='offer_end'),
    path('offer/<int:pk>/delete/', views.offer_delete, name='offer_delete'),


    path('delivery_done/<int:need_id>/', views.delivery_done, name='delivery_done'),  

    path('stock/', views.admin_stocks, name='admin_stocks'), 
    path('stock/manage/', views.manage_stock_view, name='manage_stock'),
    path('warehouse/manage/', views.warehouse_stocks, name='warehouse_stocks'),
    path('warehouse/summary/', views.all_order_summary, name='all_warehouse_stocks'),
    path('factory/summary/', views.factory_summary, name='admin_summary'), 
    
 

]

