from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
import json
import datetime
import random
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .utils import cookieCart, cartData, guestOrder, render_to_pdf
from django.template.loader import get_template
from .forms import UserRegistrationForm, EmailSubForm, FeedbackForm

# Create your views here.


def home(request):
    data = cartData(request)
    cartItems = data['cartItems']
    email_form = EmailSubForm()
    feedback_form = FeedbackForm()
    products = Product.objects.all().order_by('-quantity_available')
    products = products[:7]  
    context = {'cartItems':cartItems,'products':products,'email_form':email_form,'feedback_form':feedback_form}
    return render(request, 'index.html', context)

def shop(request, category_slug=None):
    data = cartData(request)
    cartItems = data['cartItems']
    
        
    category = None
    categories = Category.objects.all()
    products_list = Product.objects.all()
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_list = products_list.filter(category=category)
        paginator = Paginator(products_list, 12)
        try:
            products = paginator.page(page)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        except:
            products = paginator.page(1)
    else:
        try:
            products = paginator.page(page)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        except:
            products = paginator.page(1)
        
    context = {'categories':categories,'products':products, 'cartItems':cartItems, 'category':category, 'page':page}
    return render(request, 'shop.html', context)

def product_detail(request, category_slug, slug):
    data = cartData(request)
    cartItems = data['cartItems']
    
    items = data['items']
    product = Product.objects.get(slug=slug)
    category = product.category
    products = Product.objects.all().filter(category=category)
    context = {'product':product,'cartItems':cartItems,'items':items,'products':products}    
    return render(request,'product.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items,'order':order, 'cartItems':cartItems}
    return render(request,'cart.html', context) 

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items,'order':order, 'cartItems':cartItems}
    return render(request,'checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('productId', productId)

    customer, created = Customer.objects.get_or_create(user=request.user, name=request.user.first_name, email=request.user.email)
    
    product= Product.objects.get(id=productId)
    
    cart, created = Cart.objects.get_or_create(customer=customer,complete=False)
    cartItem , created = CartItem.objects.get_or_create(cart=cart, product=product)

    if action == 'add':
        if cartItem.quantity >= cartItem.product.quantity_available:
            cartItem.quantity = cartItem.product.quantity_available
            cartItem.save()
        else:
            cartItem.quantity = (cartItem.quantity + 1)
            cartItem.save()
    elif action == 'remove':
        cartItem.quantity = (cartItem.quantity - 1)
        cartItem.save()
    elif action == 'delete':
        cartItem.delete()
    
    if cartItem.quantity <= 0:
        cartItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transactionId = datetime.datetime.now().timestamp()
    num = random.randint(100,999)
    transactionId = str(transactionId).split('.')[0] + str(num)
    transactionId = int(transactionId)
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
        order, created = Order.objects.get_or_create(customer=customer, paid=False)
        for item in cart.cartitem_set.all():
            product = Product.objects.get(id=item.product.id)
            orderItem = OrderItem.objects.create(
                product = product,
                order = order,
                quantity = item.quantity
            )
        cart.complete = True
        cart.save()
        ShippingAddress.objects.create(customer=customer, 
        order=order, 
        address=data['shipping-info']['address'],
        city=data['shipping-info']['city'],
        state=data['shipping-info']['state'],
        zipcode=data['shipping-info']['zipcode']
        )
    else:
        customer, order = guestOrder(request, data)


    total = float(data['user-info']['total'])
    order.transaction_id = transactionId
    if total == order.get_cart_total:
        order.paid = True
        date = datetime.datetime.strftime(datetime.datetime.now(), '%a %b %d, %Y %I:%M %p')
        order.date_ordered = date
        for order_item in order.orderitem_set.all():
            product_id = order_item.product.id
            product = Product.objects.get(id=product_id)
            product.quantity_available -= order_item.quantity
            product.save()

        order.save()
        subject = f'ORDER CONFIRMATION - Invoice no. {order.id}'
        email = order.customer.email
        print(email)
        message = f'Hello {order.customer.name}, thank you for your order!\n\nWe have received your order and we will contact you as soon as your package is being delivered. Please, find attached the invoice for your order. '
        email = EmailMessage(subject, message, 'support@cremencakes.com', (email,))
        template = get_template('admin/orders/order/pdf.html')
        context_ = {'order':order}
        html = template.render(context_)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')), result)
        
        email.attach(f'order-{order.id}.pdf',result.getvalue(), 'application/pdf')
            
        try:
            email.send()
        except:
            pass
        

    return JsonResponse('Payment Submitted', safe=False)

@login_required
def orders(request):
    customer = Customer.objects.get(user=request.user)
    print(customer)
    orders = customer.order_set.all().order_by('-date_ordered')
    
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'orders':orders,'cartItems':cartItems}
    return render(request, 'orders.html',context)


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order':order}
    return render(request, 'admin/orders/order/detail.html', context)

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order':order}
    pdf = render_to_pdf('admin/orders/order/pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        content = f"attachment; filename=order-{order.id}.pdf"
        response['Content-Disposition'] = content
        return response
        
    return HttpResponse('Not Found')

def register(request):
    if request.user.is_authenticated:
        return redirect(home)  

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        print(user_form)
        if user_form.is_valid():
            print(user_form.cleaned_data['first_name'])
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            context = {'first_name':user_form.cleaned_data['first_name']}
            return render(request, 'registration/after.html', context)   

        else:
            print('Errors: ', user_form.errors)
            context = {'user_form':user_form} 
            return render(request, 'registration/register.html', context)
    else:
        user_form = UserRegistrationForm()
        context = {'user_form':user_form}
        return render(request, 'registration/register.html', context)
            
def email_subscribe(request):
    if request.method == 'POST':
        email_form = EmailSubForm(request.POST)
        if email_form.is_valid():
            print(email_form.cleaned_data['email'])
            new_email = email_form.cleaned_data['email']
            new_subscription = EmailSubscription.objects.create(email=new_email)
            
            new_subscription.save()
            
               

        else:
            print('Errors: ', email_form.errors)
            
    return redirect('home')



def feedback(request):
    
    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            print(feedback_form.cleaned_data['message'])
            new_name = feedback_form.cleaned_data['name']
            new_email = feedback_form.cleaned_data['email']
            new_subject = feedback_form.cleaned_data['subject']
            new_message = feedback_form.cleaned_data['message']
            new_feedback = Feedback.objects.create(name=new_name,email=new_email,subject=new_subject, message=new_message)
            
            new_feedback.save()
            
               

        else:
            print('Errors: ', feedback_form.errors)
            
    return redirect('home')


