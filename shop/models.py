from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
  
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('shop_by_category',args=[self.slug])

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200,null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    slug = models.SlugField(max_length=200,db_index=True)
    quantity_available = models.PositiveIntegerField(null=True)
    price = models.FloatField()
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('product_detail',args=[self.category.slug, self.slug])


    def __str__(self):
        return self.name


class Customer(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)

    def __str__(self):
        return self.name
 

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.CharField(null=True, blank=True, max_length=250) 
    paid = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=100, null=True)


    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
 
    def __str__(self):
        return str(self.id)

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True) 
    complete = models.BooleanField(default=False, null=True, blank=False)


    @property
    def get_cart_total(self):
        cartitems = self.cartitem_set.all()
        total = sum([item.get_total for item in cartitems])
        return total

    @property
    def get_cart_items(self):
        cartitems = self.cartitem_set.all()
        total = sum([item.quantity for item in cartitems])  
        return total
 
    def __str__(self):
        return str(self.id)

class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    @property
    def get_list(self):
        q_list = [(int(q) + 1 ) for q in range(self.product.quantity_available)]
        return q_list



class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    @property
    def get_list(self):
        q_list = [(int(q) + 1 ) for q in range(self.product.quantity_available)]
        return q_list

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address