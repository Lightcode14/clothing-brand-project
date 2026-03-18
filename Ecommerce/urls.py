"""
URL configuration for Ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

    
urlpatterns = [
   path('admin/', admin.site.urls),
    path('', include('Brand.urls')),
    path("signup/", user_views.signup, name="signup"),
    path("login/", user_views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
    path("activate/<uidb64>/<token>/", user_views.activate, name="activate"),
    path('profile/', user_views.profile_view, name='profile'),
    path('profile-update/', user_views.profile_update_view, name='profile-update'),  
    path('cart/', user_views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', user_views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', user_views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', user_views.update_cart, name='update_cart'),
    path('product/<int:id>/', user_views.product_detail, name='product_detail'),
    path('checkout/', user_views.checkout, name='checkout'),
    path("pay/<int:order_id>/", user_views.initialize_payment, name="initialize-payment"),
    path("verify-payment/<int:order_id>/", user_views.verify_payment, name="verify-payment"),
    path("order-success/", user_views.order_success, name="order-success"),
    path("payment-failed/", user_views.payment_failed, name="payment-failed"),
    path('wishlist/', user_views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', user_views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', user_views.remove_from_wishlist, name='remove_from_wishlist'),
    path("wishlist/toggle/<int:product_id>/", user_views.toggle_wishlist, name="toggle_wishlist"),
    path('orders/', user_views.order_history, name='order_history'),
    path('transactions/', user_views.transactions, name='transactions'),
    
    #password urls #
    path('password-reset/', user_views.password_reset_request, name='password_reset'),
    path('reset-password/<uuid:token>/', user_views.reset_password, name='password-confirm'),
    path('password-reset/done/', TemplateView.as_view(
    template_name='users/password_reset_done.html'
), name='password_reset_done'),
path('reset_link_expired/', TemplateView.as_view(
    template_name='users/reset_link_expired.html'
), name='reset_link_expired'),

]
if settings.DEBUG:
  urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)