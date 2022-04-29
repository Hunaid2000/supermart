from django.urls import path
from . import views

urlpatterns = [    
    path('', views.home, name='home'),
    path('accounts', views.accounts, name='accounts'),
    path('logout', views.logout, name='logout'),
    path('registerstore',views.registerstore, name = 'registerstore'),
    path('addproduct',views.addproduct, name = 'addproduct'),
    path('product/<int:id>',views.productdetails, name = 'productdetails'),
    path('cart',views.cart, name = 'cart'),
]