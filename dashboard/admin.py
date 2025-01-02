from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Zone)
admin.site.register(Department)
admin.site.register(Shop)
admin.site.register(Product)
admin.site.register(Offer)
admin.site.register(Order)
admin.site.register(FinalOrder)

admin.site.register(DealerProductNeed)
admin.site.register(DealerOrder)
admin.site.register(Stock)
admin.site.register(StockItem)

