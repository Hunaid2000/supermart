from django.shortcuts import render, redirect
from django.contrib import messages
from supermartApp.models import Account, Product, ProductImages, Store


def home(request):
    if 'user_id' not in request.session:
        images = ProductImages.objects.all()
    elif 'is_seller' in request.session and request.session['is_seller'] == 1:
        images = ProductImages.objects.filter(product__store__seller_id=request.session['user_id'])  
    return render(request, 'home.html', {'images':images})

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
            request.session['is_seller'] = user.is_seller
            return redirect('home')
        else:
            messages.error(request, 'Incorrect Email/Password')    
    return render(request, 'accounts.html')

def registerstore(request):
    if request.method == 'POST':
        store_name = request.POST['store_name']
        contact = request.POST['contact']
        location = request.POST['location']
        seller = Account.objects.get(pk=request.session['user_id'])
        if Store.objects.filter(store_name=store_name).exists():
            messages.error(request, 'This Store name is already in use')
            return redirect('registerstore')
        store = Store(store_name=store_name, contact=contact, location=location, seller=seller)
        store.save()  
    return render(request, 'registerstore.html')

def addproduct(request):
    if request.method == 'POST':
        name = request.POST['name']
        brand = request.POST['brand']
        price = request.POST['price']
        total_stock = request.POST['total_stock']
        small = request.POST['small']
        if small == '':
            small = 0
        small = int(small)            
        medium = request.POST['medium']
        if medium == '':
            medium = 0
        medium = int(medium)
        large = request.POST['large']
        if large == '':
            large = 0
        large = int(large)
        description = request.POST['description']
        images = request.FILES.getlist('images')
        store = Store.objects.get(pk=request.POST['storename'])        
        product = Product(name=name, brand=brand, price=price, total_stock=total_stock, small=small, medium=medium, large=large, description=description, store=store)
        product.save()  
        for img in images:
            productImage = ProductImages(image=img, product=product)
            print(productImage)
            productImage.save()
    stores = Store.objects.filter(seller_id=request.session['user_id'])
    return render(request, 'addproduct.html', {'stores':stores})

def productdetails(request, id):
    product = Product.objects.filter(pk=id)
    images = ProductImages.objects.filter(product_id=id)  
    return render(request, 'productdetails.html', {'product':product, 'images':images})