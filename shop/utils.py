import json
from .models import *
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('CART: ', cart)
    items = []
    order= {'get_cart_total':0,'get_cart_items':0}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'image':{'url':product.image.url}
                },
                'quantity': cart[i]['quantity'],
                'get_total': total
            }

            items.append(item)
        except:
            pass 
    
    return {'cartItems': cartItems, 'order':order, 'items': items}


def cartData(request):

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, name=request.user.first_name, email=request.user.email)
        cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
        items = cart.cartitem_set.all()
        cartItems = cart.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cart = cookieData['order']
        items = cookieData['items']
    return {'cartItems':cartItems,'order': cart, 'items': items}
 


def guestOrder(request, data):
    name = data['user-info']['name']
    email = data['user-info']['email']
    address = data['shipping-info']['address']
    city = data['shipping-info']['city']
    state = data['shipping-info']['state']
    zipcode = data['shipping-info']['zipcode']

    cookieData = cookieCart(request)
    items = cookieData['items'] 

    customer, created = Customer.objects.get_or_create(email=email, name=name)
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False
    )

    ShippingAddress.objects.create(customer=customer, 
        order=order, 
        address=data['shipping-info']['address'],
        city=data['shipping-info']['city'],
        state=data['shipping-info']['state'],
        zipcode=data['shipping-info']['zipcode']
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity']
        )

    return customer, order


def render_to_pdf(template_src, context={}):
    template = get_template(template_src)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue())
    return None