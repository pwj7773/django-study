from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Order
from .models import User
# Create your views here.

def home(request) :
    return HttpResponseRedirect('order/')

def index(request) :
    return render(request,'order/index.html')

def add_order(request) :
    if request.method == 'GET' :
        return render(request,'order/order_form.html')
    
    else :
        order_text = request.POST['order_text']
        price = request.POST['price']
        address = request.POST['address']

        Order.objects.create(
            order_text = order_text,
            price = price,
            address = address
        )

    return HttpResponseRedirect('/order/')

def order_list(requset) :
    order_list = Order.objects.all()

    context = {
        'order_list' : order_list
    }
    return render(requset, 'order/order_list.html' , context)

def delete(request, id) :
    Order.objects.get(id = id).delete()

    return HttpResponseRedirect('/order/order_list/')

def update(request,id) :

    order = Order.objects.get(id = id)

    if request.method == 'GET' :
        context = {
            'order' : order
        }
        return render(request, 'order/update_form.html',context)
    else :
        order.order_text = request.POST['order_text']
        order.price = request.POST['price']
        order.address = request.POST['address']
        order.save()

        return HttpResponseRedirect('/order/order_list/')
    
def search(request) :
    get_text = request.GET['order_text']
    option = request.GET['option']
    if option == 'all' :
        order_list = Order.objects.filter(order_text = get_text)
    elif option == 'part':
        order_list = Order.objects.filter(order_text__contains = get_text)
    elif option == 'start' :
        order_list = Order.objects.filter(order_text__startswith = get_text)
    context = {
        'order_list' : order_list
    }
    return render(request,'order/order_list.html',context)

def show(request,id) :
    order = Order.objects.get(id = id)
    context = { 
        'order' : order,
        'text_list' : order.order_text.split(",")
    }
    return render(request,'order/order_show.html/',context)

def signup(request) :
    if request.method == 'GET' :
        return render(request,'order/signup.html/')
    else :
        user_id =request.POST['user_id']
        password = request.POST['password']
        email = request.POST['email']
        if User.objects.filter(user_id = user_id) :
            context = {
                'result' : "중복된 아이디입니다."
            }
            return render(request,'order/signup.html/',context)
        else :
            User.objects.create(
                user_id = user_id,
                password = password,
                email = email
            )
            return HttpResponseRedirect('/order/')

def login(request) :
    if request.method == 'GET' :
        return render(request,'order/login.html/')
    else :
        input_id = request.POST['user_id']
        input_password = request.POST['password']
        if User.objects.filter(user_id = input_id) :
            getUser = User.objects.get(user_id = input_id)
            if getUser.password == input_password :
                request.session['login'] = True
                context = {'result' : request.session.get('login')}
                return render(request,'order/index.html',context)
            else :
                request.session['login'] = False
                context = {'result' : '로그인 실패'}
                return render(request,'order/login.html/',context)
            
def logout(request) :
    del request.session['login']
    return HttpResponseRedirect('/order/')

