from django.shortcuts import render, redirect
from dashboard.models import *
from django.contrib.auth.decorators import login_required
from dashboard.decorators import auth_users, allowed_users
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['RSM'])
def sr_orders(request):
    
    final_orders = FinalOrder.objects.all().order_by('-created_at')
   
    paginator = Paginator(final_orders, 20)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)

    for final_order in page_obj:
        filtered_orders = final_order.orders.all().order_by('-created_at')
        final_order.filtered_orders = filtered_orders

        # Calculate the totals for the filtered orders
        total_quantity = sum(order.order_quantity for order in filtered_orders)
        total_net_amount = sum(order.order_quantity * order.name.product_tp for order in filtered_orders)
        total_gross_amount = sum(order.order_quantity * order.name.discounted_price(order.created_at) for order in filtered_orders)
        total_discount_amount = sum(order.order_quantity * order.name.discount(order.created_at) for order in filtered_orders)

        # Attach the totals to the final_order object for use in the template
        final_order.total_quantity = total_quantity
        final_order.total_net_amount = total_net_amount
        final_order.total_gross_amount = total_gross_amount
        final_order.total_discount_amount = total_discount_amount

    # Pass the final orders to the template
    is_rsm = request.user.groups.filter(name='RSM').exists()
    context = {
        'final_orders': page_obj,
        'is_rsm': is_rsm
    }
    
    return render(request, 'rsm/sr_orders.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['RSM'])
def dealer_demand_check(request):
   
    # Get all FinalOrder objects
    dealer_demand = DealerOrder.objects.all().order_by('-created_at')

    for final_order in dealer_demand:
        filtered_orders = final_order.products.all().order_by('-created_at')
        final_order.filtered_orders = filtered_orders

        # Calculate the totals for the filtered orders
        total_quantity = sum(order.demand_quantity for order in filtered_orders)
        total_amount = sum(order.product.product_dp for order in filtered_orders)
        total_net_amount = sum(order.demand_quantity * order.product.product_dp for order in filtered_orders)
        total_gross_amount = sum(order.demand_quantity * order.product.product_dp for order in filtered_orders)

        # Attach the totals to the final_order object for use in the template
        final_order.total_quantity = total_quantity
        final_order.total_amount = total_amount
        final_order.total_net_amount = total_net_amount
        final_order.total_gross_amount = total_gross_amount

    # Pass the final orders to the template
    is_rsm = request.user.groups.filter(name='RSM').exists()
    context = {
        'final_orders': dealer_demand,
        'is_rsm': is_rsm
    }
    
    return render(request, 'rsm/dealer_demands.html', context)   




###HOS###########HOS#########HOS######HOS#####HOS####HOS############HOS########HOS###################HOS#######HOS##############HOS############HOS###################HOS##################HOS##########################################################################

