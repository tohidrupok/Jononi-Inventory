from django.shortcuts import render, redirect
from dashboard.models import *
from django.contrib.auth.decorators import login_required
from dashboard.decorators import auth_users, allowed_users
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator


# Create your views here.
@login_required(login_url='user-login')
@allowed_users(allowed_roles=['HOS'])
def check(request):
   
    is_hos = request.user.groups.filter(name='HOS').exists()
    context = {
        'is_hos': is_hos
    }
    
    return render(request, 'hos/check.html', context)   

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['HOS'])
def hos_dealer_demand_check(request):
   
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
    is_hos = request.user.groups.filter(name='HOS').exists()
    context = {
        'final_orders': dealer_demand,
        'is_hos': is_hos
    }
    
    return render(request, 'hos/dealer_demands.html', context)   