from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Product, Order, Zone, Shop , FinalOrder, DealerProductNeed, DealerOrder ,Offer, Stock , StockItem
from .forms import ProductForm, OrderForm , ShopForm , DateSelectForm , DealerProductNeedForm , editOrderForm, editdemandForm, noteOrderForm, ExpenceOrderForm, ExpenceDemandForm, PaidDemandForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import auth_users, allowed_users

from django.http import JsonResponse
from django.utils import timezone
from django.forms import formset_factory
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.db import transaction

from django.core.paginator import Paginator
from django.utils import timezone 
from django.urls import reverse

@login_required(login_url='user-login')
def base(request):
    is_sr = request.user.groups.filter(name='SR').exists()
    is_dealer = request.user.groups.filter(name='DEALER').exists()
    is_rsm = request.user.groups.filter(name='RSM').exists()
    is_hos = request.user.groups.filter(name='HOS').exists() 
    is_finance = request.user.groups.filter(name='Finance').exists() 
    print(is_sr)
    print(is_dealer)
    context = {
        'is_sr': is_sr,
        'is_dealer': is_dealer,
        'is_rsm': is_rsm,
        'is_hos': is_hos,
        'is_finance': is_finance,

    }
    return render(request, 'dashboard/base.html', context)

#For Warehouse 
@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR']) 

def warehouse(request):
    ProductOrderFormset = formset_factory(OrderForm, extra=1)
    shops = Shop.objects.all()
    selected_shop = None
    is_sr = request.user.groups.filter(name='SR').exists()

    if request.method == 'POST':
        formset = ProductOrderFormset(request.POST)
        selected_shop_id = request.POST.get('selected_shop')

        if selected_shop_id:
            try:
                selected_shop = Shop.objects.get(id=selected_shop_id)
            except Shop.DoesNotExist:
                selected_shop = None

        if formset.is_valid() and selected_shop:
            
            # Server-side validation for each order form
            for form in formset:
                if not form.cleaned_data.get('name') or not form.cleaned_data.get('order_quantity'):
                    form.add_error(None, "পণ্য এবং পরিমাণ অবশ্যই প্রদান করতে হবে।")

            # If there are any errors in the formset
            if any(form.errors for form in formset):
                return render(request, 'dashboard/index.html', {'shops': shops, 'selected_shop': selected_shop, 'formset': formset, 'is_sr': is_sr}) 
            
            
            with transaction.atomic():
                final_order = FinalOrder.objects.create(
                    customer=request.user,
                    shop=selected_shop
                )

                for form in formset:
                    order = form.save(commit=False)
                    order.customer = request.user
                    order.shop = selected_shop
                    order.save()
                    final_order.orders.add(order)

                final_order.save()

            return redirect('order_manage')
    else:
        formset = ProductOrderFormset()
    is_sr = request.user.groups.filter(name='SR').exists()
    context = {
        'shops': shops,
        'selected_shop': selected_shop,
        'formset': formset,
        'is_sr': is_sr,
    }

    return render(request, 'dashboard/index.html', context)

def get_product_tp(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({'product_tp': product.product_tp}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404) 
    
    
    
@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR']) 

def index(request):
    today = timezone.now().date()  
    selected_date = request.GET.get('selected_date', today) 
    zones = Zone.objects.values('name').distinct()
    shops = None
    selected_shop = None 
    shop_orders = None

    ProductOrderFormset = formset_factory(OrderForm, extra=1)

    # Retrieve zone, district, thana, and area from session if available
    selected_zone_name = request.session.get('selected_zone_name')
    selected_zone_district = request.session.get('selected_zone_district')
    selected_zone_thana = request.session.get('selected_zone_thana')
    selected_zone_area = request.session.get('selected_zone_area')

    if request.method == 'GET':
        zone_name = request.GET.get('zone_name')
        zone_district = request.GET.get('zone_district')
        zone_thana = request.GET.get('zone_thana')
        zone_area = request.GET.get('zone_area')

        if zone_name:
            # Store these selections in session to retain them after redirect
            request.session['selected_zone_name'] = zone_name
            request.session['selected_zone_district'] = zone_district
            request.session['selected_zone_thana'] = zone_thana
            request.session['selected_zone_area'] = zone_area
            
            # Filter the zones based on the selections
            filtered_zones = Zone.objects.filter(
                name=zone_name,
                district=zone_district,
                thana=zone_thana,
                area=zone_area
            )
            shops = Shop.objects.filter(zone__in=filtered_zones)

        # Retrieve selected shop from session if available
        if 'selected_shop_id' in request.session:
            try:
                selected_shop = Shop.objects.get(id=request.session['selected_shop_id'])
                shop_orders = Order.objects.filter(shop=selected_shop, customer=request.user, created_at__date=selected_date).order_by('-created_at')
            except Shop.DoesNotExist:
                selected_shop = None
                shop_orders = None

    if request.method == 'POST':
        formset = ProductOrderFormset(request.POST)
        selected_shop_id = request.POST.get('selected_shop')

        if selected_shop_id:
            try:
                selected_shop = Shop.objects.get(id=selected_shop_id)
                request.session['selected_shop_id'] = selected_shop_id  # Store in session
            except Shop.DoesNotExist:
                selected_shop = None

        if formset.is_valid() and selected_shop:
            with transaction.atomic():  
                final_order = FinalOrder.objects.create(
                    customer=request.user,
                    shop=selected_shop
                )

                for form in formset:
                    obj = form.save(commit=False)
                    obj.customer = request.user
                    obj.shop = selected_shop
                    obj.save()  

                    final_order.orders.add(obj)

                final_order.save()

            # Redirect after processing the formset with session variables carried over
            return redirect(f'{reverse("dashboard-index")}?zone_name={selected_zone_name}&zone_district={selected_zone_district}&zone_thana={selected_zone_thana}&zone_area={selected_zone_area}')

    else:
        formset = ProductOrderFormset()

    is_sr = request.user.groups.filter(name='SR').exists()

    # Calculate totals after checking for shop orders
    total_net_amount = total_gross_amount = total_quantity = total_discount_amount = 0
    if shop_orders:
        for order in shop_orders:
            total_net_amount += order.net_amount()
            total_gross_amount += order.gross_amount()
            total_discount_amount += order.discount_amount()
            total_quantity += order.order_quantity   

    context = {
        'is_sr': is_sr,
        'formset': formset,
        'zones': zones,
        'shops': shops,
        'selected_shop': selected_shop,
        'shop_orders': shop_orders,
        'total_net_amount': total_net_amount,
        'total_gross_amount': total_gross_amount,
        'total_discount_amount': total_discount_amount,
        'total_quantity': total_quantity,
        'selected_date': selected_date,  
        'today': today,
        'selected_zone_name': selected_zone_name,
        'selected_zone_district': selected_zone_district,
        'selected_zone_thana': selected_zone_thana,
        'selected_zone_area': selected_zone_area,
    }

    return render(request, 'dashboard/index.html', context)


def get_districts(request):
    zone_name = request.GET.get('zone_name')
    if zone_name:
        districts = Zone.objects.filter(name=zone_name).values_list('district', flat=True).distinct()
        return JsonResponse({'districts': list(districts)})
    return JsonResponse({'districts': []})

def get_thanas(request):
    district_name = request.GET.get('district_name')
    if district_name:
        thanas = Zone.objects.filter(district=district_name).values_list('thana', flat=True).distinct()
        return JsonResponse({'thanas': list(thanas)})
    return JsonResponse({'thanas': []})

def get_areas(request):
    thana_name = request.GET.get('thana_name')
    if thana_name:
        areas = Zone.objects.filter(thana=thana_name).values_list('area', flat=True).distinct()
        return JsonResponse({'areas': list(areas)})
    return JsonResponse({'areas': []})



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])

def shops(request):
    shops = Shop.objects.all()
    shop_count = shops.count()

    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            form.save()
            shop_name = form.cleaned_data.get('shop_name')
            messages.success(request, f'{shop_name} has been added')
            return redirect('add-shope')
    else:
        form = ShopForm()
    
    is_sr = request.user.groups.filter(name='SR').exists()
    context = {
        'shops': shops,
        'form': form,       
        'shop_count': shop_count,  
        'is_sr': is_sr,     
    }
         
    return render(request, 'dashboard/add_shop.html', context) 

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR']) 

def edit_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == 'POST':
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, f'Shop "{shop.shop_name}" has been updated successfully.')
            return redirect('add-shope')
    else:
        form = ShopForm(instance=shop)

    context = {
        'form': form,
        'shop': shop,
    }
    return render(request, 'dashboard/edit_shop.html', context)

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR']) 

def delete_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == 'POST':
        shop_name = shop.shop_name
        shop.delete()
        messages.success(request, f'Shop "{shop_name}" has been deleted successfully.')
        return redirect('add-shope')

    context = {
        'shop': shop,
    }
    return render(request, 'dashboard/confirm_delete.html', context) 



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def daily_report(request):
    today = timezone.now()
    start_date = None
    end_date = None

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        
        if not start_date and end_date:
            start_date = end_date

        
        if not end_date and start_date:
            end_date = start_date
        
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

            date_range = (min(start_date, end_date), max(start_date, end_date))
            orders_today = Order.objects.filter(created_at__date__range=date_range, customer=request.user)
        else:
            orders_today = Order.objects.none()  
    else:
        orders_today = Order.objects.filter(created_at__date=today.date(), customer=request.user)

    total_quantity = sum(order.order_quantity for order in orders_today)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    context = {
        'orders_today': orders_today,
        'total_quantity': total_quantity,
        'today': today,
        'start_date': start_date,
        'end_date': end_date,
        'is_sr': is_sr,
    }
    
    return render(request, 'dashboard/daily_report.html', context)

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER','SR'])
def active_offer_list(request):
    now = timezone.now()
    active_offers = Offer.objects.filter(start_date__lte=now, end_date__gte=now)

    is_sr = request.user.groups.filter(name='SR').exists()
    is_dealer = request.user.groups.filter(name='DEALER').exists()
    return render(request, 'dashboard/active_offer_list.html', {'offers': active_offers,'is_sr': is_sr,'is_dealer': is_dealer}) 


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def order_manage(request):
    now = timezone.now()    
    orders = FinalOrder.objects.filter(customer=request.user).order_by('-created_at')

    paginator = Paginator(orders, 15)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
       

    for final_order in page_obj:
        filtered_orders = final_order.orders.filter(customer=request.user).order_by('-created_at')
        final_order.filtered_orders = filtered_orders

        total_quantity = sum(order.order_quantity for order in filtered_orders)
        total_net_amount = sum(order.order_quantity * order.product_tp for order in filtered_orders if order.order_quantity is not None and order.product_tp is not None)
        total_gross_amount = sum(order.order_quantity * order.name.discounted_price(order.created_at) for order in filtered_orders)
        total_discount_amount = sum(order.order_quantity * order.name.discount(order.created_at) for order in filtered_orders)

        final_order.total_quantity = total_quantity
        final_order.total_net_amount = total_net_amount
        final_order.total_gross_amount = total_gross_amount
        final_order.total_discount_amount = total_discount_amount

 
    is_sr = request.user.groups.filter(name='SR').exists()

    return render(request, 'dashboard/order_manage.html', {'page_obj': page_obj, 'is_sr': is_sr})



def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = editOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully!")
            return redirect('order_manage')
    else:
        form = editOrderForm(instance=order)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': order, 'is_sr': is_sr})


def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, "Order deleted successfully!")
        return redirect('order_manage')  
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/confirm_delete_order.html', {'order': order,'is_sr': is_sr})




from django.http import Http404
@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])

def confirm_product(request, need_id):
    try:
        # Get the Order object
        need = get_object_or_404(Order, id=need_id)
        
        # Validate the product
        if not need.name:
            messages.error(request, "The specified product does not exist.")
            return redirect('order_manage')
        
        # Check for user's stock
        try:
            stock = get_object_or_404(Stock, customer=request.user)
        except Http404:
            messages.error(request, "আপনার জন্য নির্ধারিত কোনো স্টক নেই।")
            return redirect('order_manage')

        # Attempt to retrieve the stock item
        try:
            stock_item = get_object_or_404(StockItem, stock=stock, product=need.name)
        except Http404:
            messages.error(request, "এই পণ্যের জন্য কোনো স্টক তালিকাভুক্ত নেই।")
            return redirect('order_manage')

        # Process the order if it is in 'Pending' status
        if need.status == 'Pending':
            if stock_item.sell_stock(need.order_quantity):
                # Update need status
                need.status = "Delivered"

                # Update dealer account balance
                dealer_account, _ = Account.objects.get_or_create(user=request.user)
                dealer_account.update_balance(need.net_amount())

                # Save updated models
                stock_item.save()
                need.save()

                messages.success(request, "পণ্য বিতরণ সম্পন্ন এবং স্টক হালনাগাদ করা হয়েছে।")
            else:
                messages.error(request, "অর্ডার পূরণের জন্য পর্যাপ্ত স্টক নেই।")
                return redirect('order_manage')

        else:
            messages.info(request, "This order has already been processed.")
            return redirect('order_manage')

    except Stock.DoesNotExist:
        messages.error(request, "You do not have an associated stock.")
        return redirect('order_manage')

    return redirect('order_manage')



# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from xhtml2pdf import pisa

# def generate_pdf(request, order_id):
#     # Fetch the `final_order` using the `order_id`
#     final_order = FinalOrder.objects.get(id=order_id)
   
    
#     filtered_orders = final_order.orders.filter(customer=request.user).order_by('-created_at')
#     final_order.filtered_orders = filtered_orders

#     total_quantity = sum(order.order_quantity for order in filtered_orders)
#     total_net_amount = sum(order.order_quantity * order.product_tp for order in filtered_orders if order.order_quantity is not None and order.product_tp is not None)

#     final_order.total_quantity = total_quantity
#     final_order.total_net_amount = total_net_amount
    
#     # Render the HTML template with context data
#     html = render_to_string('dashboard/order_details_pdf.html', {'final_order': final_order})

#     # Create a PDF response
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf"'

#     # Generate the PDF
#     pisa_status = pisa.CreatePDF(html, dest=response)

#     # If an error occurred
#     if pisa_status.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')

#     return response

def generate_pdf(request, order_id):
    
    final_order = FinalOrder.objects.get(id=order_id)
       
    filtered_orders = final_order.orders.filter(customer=request.user).order_by('-created_at')
    final_order.filtered_orders = filtered_orders

    total_quantity = sum(order.order_quantity for order in filtered_orders)
    total_net_amount = sum(order.order_quantity * order.product_tp for order in filtered_orders if order.order_quantity is not None and order.product_tp is not None)

    final_order.total_quantity = total_quantity
    final_order.total_net_amount = total_net_amount 
    
    return render(request, 'dashboard/order_details_pdf.html', {'final_order': final_order})

from datetime import datetime, timedelta

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def payment_commission(request):
    # Get today's date
    today = now().date()
       
    # Fetch today's orders or filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Convert strings to datetime.date objects
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            # Handle invalid date format gracefully
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
    
        # Ensure start_date and end_date are converted to datetime objects
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
    
        final_orders = DealerOrder.objects.filter(
            created_at__range=[start_datetime, end_datetime],
            dealer=request.user
        ).order_by('-created_at')
    else:
        # Handle case where no dates are provided
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
    
        final_orders = DealerOrder.objects.filter(
            created_at__range=[today_start, today_end],
            dealer=request.user
        ).order_by('-created_at') 

    # Prepare data for the template
    orders_data = []
    total_gross = 0
    total_note = 0
    total_expense_Amount = 0
    total_commission = 0
    total_qnt = 0

    for order in final_orders:
        gross_amount = order.net_amount() 
        commission = order.calculate_commission()
        qnt= order.total_demand_quantity()
        note_amount = order.note_amount or 0
        expense_Amount = order.expense_Amount or 0 

        total_gross += gross_amount
        total_note += note_amount
        total_expense_Amount += expense_Amount
        total_commission += commission
        total_qnt += qnt
 
        orders_data.append({
            'id': order.id,
            
            'sr': order.dealer,
            'created_at': order.created_at,
            'gross_amount': gross_amount,
            'note_amount': note_amount,
            'expense_Amount': expense_Amount,
            'commission': commission,
            'qnt': qnt,
            'total': note_amount - gross_amount
        })

    # Summation of gross and note amounts
    overall_total = total_note - total_gross
    
    is_sr = request.user.groups.filter(name='SR').exists()
    is_admin = request.user.groups.filter(name='Admin').exists()
    is_finance = request.user.groups.filter(name='Finance').exists() 
    context = {
        'orders_data': orders_data,
        'total_gross': total_gross,
        'total_note': total_note,
        'total_expense_Amount': total_expense_Amount ,
        'total_commission': total_commission ,
        'total_qnt': total_qnt ,
        'overall_total': overall_total,
        'start_date': start_date,
        'end_date': end_date,
        
        'is_sr': is_sr,
        'is_admin': is_admin,
        'is_finance': is_finance,
    }

    return render(request, 'dashboard/demand_commission_payment.html', context)

    


#######Dealer#########################Dealer Start ############################# Dealer Start #######################Dealer Start ########################Dealer Start ####################
from .models import Order, Product, Shop, Zone
from user.models import Profile

def get_orders_for_dealer_by_product_and_zone(dealer_zones, dealer_products):

    matching_orders = FinalOrder.objects.filter(
        orders__shop__zone__in=dealer_zones ,
        orders__name__in=dealer_products 
         
    ).distinct().order_by('-created_at')
    return matching_orders

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def dealer_orders_view(request):
    user = request.user  
    dealer_profile = Profile.objects.get(customer=user)  

    dealer_zones = dealer_profile.zones.all()  
    dealer_products = dealer_profile.products.all()  

    final_orders = get_orders_for_dealer_by_product_and_zone(dealer_zones, dealer_products)

    for final_order in final_orders:
        filtered_orders = final_order.orders.filter(name__in=dealer_products).order_by('-created_at')
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


    is_sr = request.user.groups.filter(name='SR').exists()

    context = {
        'final_orders': final_orders,
        'is_sr': is_sr,
    }
 
    return render(request, 'dashboard/dealer_sr_order_view.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def demand(request):
    is_sr = request.user.groups.filter(name='SR').exists()
    ProductDemandFormset = formset_factory(DealerProductNeedForm, extra=1)  

    if request.method == 'POST':
        formset = ProductDemandFormset(request.POST)

        if formset.is_valid():
            
            for form in formset:
                if not form.cleaned_data.get('product') or not form.cleaned_data.get('demand_quantity'):
                    form.add_error(None, "পণ্য এবং পরিমাণ অবশ্যই প্রদান করতে হবে।")

            # If there are any errors in the formset
            if any(form.errors for form in formset):
                return render(request, 'dashboard/dealer_requesr_demand.html', {'formset': formset, 'is_sr': is_sr,}) 
                
                
            with transaction.atomic():
             
                dealer_order = DealerOrder(dealer=request.user)
                dealer_order.save()
             
                for form in formset:
                    product_need = form.save(commit=False)
                    product_need.dealer = request.user 
                    product_need.status = 'Pending'
                    product_need.save() 
               
                    dealer_order.products.add(product_need)

                dealer_order.save()
        
            return redirect('demand_check')

    is_sr = request.user.groups.filter(name='SR').exists()
    formset = ProductDemandFormset()  

    context = {
        'formset': formset,
        'is_sr': is_sr,
    }

    return render(request, 'dashboard/dealer_requesr_demand.html', context) 



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def edit_demand(request, pk):
    order = get_object_or_404(DealerProductNeed, pk=pk)
    if request.method == 'POST':
        form = editdemandForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Demand updated successfully!")
            return redirect('demand_check')
    else:
        form = editdemandForm(instance=order)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': order, 'is_sr': is_sr})



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def delete_demand(request, pk):
    demand = get_object_or_404(DealerProductNeed, pk=pk)
    if request.method == 'POST':
        demand.delete()
        messages.success(request, "Demand deleted successfully!")
        return redirect('demand_check')  
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/confirm_delete_order.html', {'order': demand,'is_sr': is_sr}) 



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def demand_request_check(request):
    user = request.user
    
    dealer_demand = DealerOrder.objects.filter(dealer=user).order_by('-created_at')
    
    for final_order in dealer_demand:
        filtered_orders = final_order.products.all()
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

    # Implement pagination
    paginator = Paginator(dealer_demand, 20)  
    page_number = request.GET.get('page')
    paginated_orders = paginator.get_page(page_number)

    is_sr = request.user.groups.filter(name='SR').exists()
    context = {
        'final_orders': paginated_orders,
        'is_sr': is_sr,
    }
    
    return render(request, 'dashboard/dealer_demand_check.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def user_stocks(request):

    stocks = Stock.objects.filter(customer=request.user).prefetch_related('stock_items')

    is_sr = request.user.groups.filter(name='SR').exists()
    context = {
        'stocks': stocks,
        'is_sr': is_sr,
    }
    return render(request, 'dashboard/dealer_stocks.html', context)


from finance.models import Account , Credit , TransactionHistory
from django.utils.timezone import now

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def reached_product(request, need_id):
    # Get the DealerProductNeed object
    need = get_object_or_404(DealerProductNeed, id=need_id)

    # Ensure the product exists
    if not need.product:
        messages.error(request, "The specified product does not exist.")
        return redirect('demand_check')

    # Ensure the logged-in user has an associated stock
    stock, created = Stock.objects.get_or_create(customer=request.user)

    # Find or create the stock item for the product
    stock_item, created = StockItem.objects.get_or_create(
        stock=stock,
        product=need.product,
        defaults={"available_stock": 0, "reserved_stock": 0}
    )
   
   
    # Update the need's status
    if need.status == 'Admin_Approve':
        stock_item.add_stock(need.demand_quantity)
        need.status = "Received"
        need.dealer_flag= True

        delear_account, created = Account.objects.get_or_create(user=request.user)
        delear_account.update_balance(need.gross_amount())
        
        stock_item.save()

        Credit.objects.create(
            type='order_price',
            amount=need.gross_amount(),
            description=f"Dealer {request.user}, Demand price for product:  [{need.product.product_code}, {need.product.name}]",
            date=now()
        ) 

        TransactionHistory.objects.create( 
            transaction_type='credit',
            details = 'order_price',
            amount=need.gross_amount(),
            description=f"Dealer {request.user}, Demand price for Product Code: [{need.product.product_code}], Product Name: [{need.product.name}]",
            date=now()
            
        ) 
        messages.success(request, "পণ্য গ্রহণ সফল এবং স্টক আপডেট হয়েছে।")

    need.save()
 
    return redirect('demand_check')   

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def order_note(request, pk):
    order = get_object_or_404(FinalOrder, pk=pk)
    if request.method == 'POST':
        form = noteOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully!")
            return redirect('order_manage')
    else:
        form = noteOrderForm(instance=order)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': order, 'is_sr': is_sr})  

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def order_cost(request, pk):
    order = get_object_or_404(FinalOrder, pk=pk)
    if request.method == 'POST':
        form = ExpenceOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully!")
            return redirect('order_manage')
    else:
        form = ExpenceOrderForm(instance=order)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': order, 'is_sr': is_sr}) 


from datetime import datetime, timedelta  

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR','Admin'])
def order_summary(request):
    # Get today's date
    today = now().date()
       
    # Fetch today's orders or filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Convert strings to datetime.date objects
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
    
        # Convert to datetime objects for range filtering
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
    
        final_orders = FinalOrder.objects.filter(
            customer=request.user,
            created_at__range=[start_datetime, end_datetime]
        ).order_by('-created_at')
    else:
        # Handle case where only today's date is used
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
    
        final_orders = FinalOrder.objects.filter(
            customer=request.user,
            created_at__range=[today_start, today_end]
        ).order_by('-created_at')

    # Prepare data for the template
    orders_data = []
    total_gross = 0
    total_net = 0
    total_note = 0
    total_expense_Amount = 0

    for order in final_orders:
        gross_amount = order.gross_amount()  
        net_amount = order.net_amount()  
        note_amount = order.note_amount or 0  
        expense_Amount = order.expense_Amount or 0 

        total_gross += gross_amount
        total_net += net_amount
        total_note += note_amount
        total_expense_Amount += expense_Amount

        orders_data.append({
            'id': order.id,
            'shop': order.shop,
            'sr': order.customer,
            'created_at': order.created_at,
            'gross_amount': gross_amount,
            'net_amount': net_amount,
            'note_amount': note_amount,
            'expense_Amount': expense_Amount,
            'total': note_amount - net_amount
        })

    # Summation of gross and note amounts
    overall_total = total_note - total_net
    
    is_sr = request.user.groups.filter(name='SR').exists()
    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'orders_data': orders_data,
        'total_gross': total_gross,
        'total_net': total_net,
        'total_note': total_note,
        'total_expense_Amount': total_expense_Amount ,
        'overall_total': overall_total,
        'start_date': start_date,
        'end_date': end_date,
        
        'is_sr': is_sr,
        'is_admin': is_admin,
    }

    return render(request, 'dashboard/order_summary.html', context)

    
    
@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def demand_paid(request, pk):
    demand = get_object_or_404(DealerOrder, pk=pk)
    if request.method == 'POST':
        form = PaidDemandForm(request.POST, instance=demand)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment updated successfully!")
            return redirect('demand_check')
    else:
        form = PaidDemandForm(instance=demand)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': demand, 'is_sr': is_sr})   

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def demand_payment(request, pk):
    demand = get_object_or_404(DealerOrder, pk=pk)
    if request.method == 'POST':
        form = PaidDemandForm(request.POST, instance=demand)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment updated successfully!")
            return redirect('payment-commission')
    else:
        form = PaidDemandForm(instance=demand)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': demand, 'is_sr': is_sr})  

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def demand_cost(request, pk):
    demand = get_object_or_404(DealerOrder, pk=pk)
    if request.method == 'POST':
        form = ExpenceDemandForm(request.POST, instance=demand)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully!")
            return redirect('demand_check')
    else:
        form = ExpenceDemandForm(instance=demand)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': demand, 'is_sr': is_sr}) 