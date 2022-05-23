from django.shortcuts import render, redirect
from django.contrib import messages
from supermartApp.models import Account, Product, ProductImages, Store, Cart, Item, Order, CardDetails, Wishlist
from django.core.mail import send_mail

def home(request):
    images = ProductImages.objects.all()
    sortvar = None
    searchtext = None
    # sort the products as demanded
    if request.method == 'POST' and 'sortby' in request.POST:
        sortvar = request.POST['sort']
        if sortvar == 'sortbyname':
            images = ProductImages.objects.all().order_by('product__name')
        elif sortvar == 'lowprice':
            images = ProductImages.objects.all().order_by('product__price')
        else:
            images = ProductImages.objects.all().order_by('-product__price')
    # search the required product by comparing titles and descriptions
    if request.method == 'POST' and 'search' in request.POST:
        searchtext = request.POST['searchbar']
        images = [img for img in images if searchtext.lower() in img.product.name.lower() or searchtext.lower() in img.product.description.lower()]
    # For seller his own products will be displayed
    if 'is_seller' in request.session and request.session['is_seller'] == 1:
        if sortvar == 'sortbyname':
            images = ProductImages.objects.filter(product__store__seller_id=request.session['user_id']).order_by('product__name')
        elif sortvar == 'lowprice':
            images = ProductImages.objects.filter(product__store__seller_id=request.session['user_id']).order_by('product__price')
        elif sortvar == 'highprice':
            images = ProductImages.objects.filter(product__store__seller_id=request.session['user_id']).order_by('-product__price')
        elif searchtext:
            images = [img for img in images if searchtext.lower() in img.product.name.lower() or searchtext.lower() in img.product.description.lower()]
        else:
            images = ProductImages.objects.filter(product__store__seller_id=request.session['user_id'])  
    return render(request, 'home.html', {'images':images})

def logout(request):
    # logout by deleting key from django session
    del request.session['user_id']
    del request.session['is_seller']
    return redirect('home')

def accounts(request):
    # the sign up checks for the validity before inserting information to the database
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
        if is_seller == 'False':
            cart = Cart(user=account, total=0)
            cart.save()
    # the login checks for the validity before user is made to login
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
    # register store checks for data validity and seller validity before inserting to database
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

# addproduct checks for data validity before inserting product to database
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

# productdetails displays the product information along with its images and allows to add product to cart and wishlist
def productdetails(request, id):
    product = Product.objects.filter(pk=id)
    images = ProductImages.objects.filter(product_id=id)
    if request.method == 'POST' and 'addtocart' in request.POST:
        quantity = request.POST['quantity']  
        quantity = int(quantity)  
        cart = Cart.objects.get(user_id=request.session['user_id'])  
        product_item = Product.objects.get(pk=id)
        item_total = quantity * product_item.price
        total = item_total + cart.total
        Cart.objects.filter(user_id=request.session['user_id']).update(total=total)
        item = Item(product=product_item, quantity=quantity, item_total=item_total, cart=cart)
        item.save() 
        messages.success(request, "Item added to Cart")
    if request.method == 'POST' and 'addtowishlist' in request.POST:        
        if(Wishlist.objects.filter(customer_id=request.session['user_id'], product=product[0])):
            messages.error(request, 'Item already in Wishlist')
            return render(request, 'productdetails.html', {'product':product, 'images':images})
        else:
            wishlist = Wishlist(customer_id=request.session['user_id'], product=product[0])
            wishlist.save()
        messages.success(request, "Item added to Wishlist")
    return render(request, 'productdetails.html', {'product':product, 'images':images})

# cart is used to display all products in user's cart and delete product from cart
def cart(request):
    if request.method == 'POST' and 'delete' in request.POST:
        product_id = request.POST['delete'] 
        item = Item.objects.get(product_id=product_id)
        item.delete()
        messages.success(request, "Item removed from Cart")
    elif request.method == 'POST' and 'next' in request.POST:
        return redirect('checkout')
    images = ProductImages.objects.all()
    cart = Cart.objects.get(user_id=request.session['user_id'])
    cartItems = Item.objects.filter(cart=cart)
    return render(request, 'cart.html', {'images':images, 'cartItems':cartItems})

# checkout takes the information about payment and shipping options validates it before inserting to database
def checkout(request):
    if request.method == 'POST':
        shipping_address = request.POST['shipping_address']
        shipping_option = request.POST['shipping_option']
        shipping_fee = 0
        order_total = 0
        if shipping_option == 'Standard':
            shipping_fee = 5
        elif shipping_option == 'Priority':
            shipping_fee = 10
        elif shipping_option == 'Express':
            shipping_fee = 15
        cart = Cart.objects.get(user_id=request.session['user_id'])
        order_total = shipping_fee + cart.total
        payment_option = request.POST['payment_option']
        order = Order(cart=cart, shipping_address=shipping_address, shipping_option=shipping_option, payment_option=payment_option, shipping_fee=shipping_fee, order_total=order_total)
        order.save()
        if payment_option == 'Card':
            accountname = request.POST['name']
            cvv = request.POST['cvv']
            expiry_date = request.POST['expdate'] + '-01'
            if CardDetails.objects.filter(user_id=request.session['user_id']).exists():
                CardDetails.objects.filter(user_id=request.session['user_id']).update(accountname=accountname, cvv=cvv, expiry_date=expiry_date)
            else:
                card = CardDetails(user_id=request.session['user_id'], accountname=accountname, cvv=cvv, expiry_date=expiry_date)
                card.save()
        messages.success(request, "Information saved Successfully")
    return render(request, 'checkout.html')

# wishlist is used to view the products in wishlist and delete it from wishlist
def wishlist(request):
    product_id = None
    if request.method == 'POST' and 'delete' in request.POST:
        product_id = request.POST['delete'] 
        item = Wishlist.objects.get(product_id=product_id)
        item.delete()
        messages.success(request, "Item removed from Wishlist")
    if 'is_seller' in request.session and request.session['is_seller'] == 1:
        sellerItems = Wishlist.objects.filter(product__store__seller=request.session['user_id'])
        recipients = [item.customer.email for item in sellerItems]
        send_mail('Product Reminder', 'Dear Customer,\n The Product you had wished for is back in stock.\nRegards', 'sellertest00@gmail.com', recipients, fail_silently=False)
        messages.success(request, "Reminders successfully sent")
        return redirect('home')
    images = ProductImages.objects.all()
    wishlistItems = Wishlist.objects.filter(customer_id=request.session['user_id'])
    return render(request, 'wishlist.html', {'images':images, 'wishlistItems':wishlistItems})