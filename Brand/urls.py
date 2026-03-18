
from django.urls import path, include
from . import views


urlpatterns=[
    path('',views.landing,name="brand-landing"),
    path('home/',views.home,name="brand-home"),
    path('new_arrivals/',views.new_arrivals,name="new_arrivals"),
    path('customer_service/',views.customer_service,name="customer-service"),
    path('categories/',views.categories,name="categories"),
    path('search/', views.search_page, name='search_page'),
   
     
]
