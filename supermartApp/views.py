from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from supermartApp.models import Account


def home(request):
    return render(request, 'home.html')

def logout(request):
    del request.session['user_id']
    return redirect('home')

def accounts(request):
    if request.method == 'POST' and 'signup' in request.POST:
        name = request.POST['name']
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            messages.error(request, 'This Email is already in use')
            return redirect('accounts')
        password = request.POST['password']
        is_seller = request.POST['is_seller']
        account = Account(name=name, email=email, password=password, is_seller=is_seller)
        account.save()  
    elif request.method == 'POST' and 'login' in request.POST:
        email = request.POST['email']
        password = request.POST['password']
        user = None
        if Account.objects.filter(email=email, password=password).exists():
            user = Account.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            return redirect('home')
        else:
            messages.error(request, 'Incorrect Email/Password')    
    return render(request, 'accounts.html')
def registerstore(request):
    return render(request, 'registerstore.html')
def addproduct(request):
    return render(request, 'addproduct.html')