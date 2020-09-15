from django.contrib import admin 
from .models import *
import csv
from datetime import datetime
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
# Register your models here.

admin.site.site_header = 'Creme n Cakes Admin Dashboard'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {'slug': ('name',)} 

class CartItemInline(admin.TabularInline):
    model = CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem

class ShippingAddressInline(admin.TabularInline):
    model = ShippingAddress

class OrderInline(admin.TabularInline):
    model = Order
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','price','quantity_available','description')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}  


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    date = datetime.today().strftime('%Y-%m-%d')
    content_disposition = f'attachment; filename = {opts.verbose_name}-{date}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response
    export_to_csv.short_description = 'Export to CSV'
  
def order_detail(obj):
    url = reverse('admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')

def order_pdf(obj):
    url = reverse('admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')
order_pdf.short_description = 'Invoice'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','customer','paid','date_ordered','transaction_id', order_detail,order_pdf)
    list_filter = ('date_ordered','paid')
    inlines = (OrderItemInline, ShippingAddressInline) 
    actions = [export_to_csv]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer','complete','date_created')
    list_filter = ('complete',)
    inlines = (CartItemInline,) 
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name','email')
    inlines = (OrderInline, ShippingAddressInline)

@admin.register(EmailSubscription)
class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email',)
   
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name','email','subject',)
    



    