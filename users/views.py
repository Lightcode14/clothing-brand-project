from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserRegisterForm,UserLoginForm, UserUpdateForm
from .models import CartItem, Order, OrderItem, Wishlist
from Brand.models import Products
import requests
from .models import Transaction
from django.conf import settings
import uuid
from django.http import JsonResponse
from .models import PasswordResetToken
from django.contrib.auth.hashers import make_password

from .forms import PasswordResetRequestForm,SetNewPasswordForm



def signup(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.is_active = False  # 👈 IMPORTANT
            user.save()

            current_site = get_current_site(request)
            subject = "Activate your account"
            message = render_to_string("users/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })

            send_mail(subject, message, None, [user.email])
            return render(request, "users/email_sent.html")
    else:
        form = UserRegisterForm()

    return render(request, "users/signup.html", {"form": form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "users/activation_success.html")
    else:
        return render(request, "users/activation_invalid.html")
def login_view(request):
    form = UserLoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            # Get next URL safely
            next_url = request.POST.get('next')

            # Only redirect to next if it's not empty or 'None'
            if next_url and next_url != 'None':
                return redirect(next_url)
            else:
                return redirect('brand-home')

    # GET request: get next parameter from query string
    next_url = request.GET.get('next')
    if next_url == 'None':  # prevent passing 'None' to template
        next_url = None

    return render(request, 'users/login.html', {
        'form': form,
        'next': next_url
    })

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def profile_update_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'users/profile_update.html', context)

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    return render(request, 'users/cart.html', {'cart_items': cart_items, 'total': total})
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Item added to cart successfully!")
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart_view')

def product_detail(request, id):
    product = get_object_or_404(Products, id=id)
    return render(request, 'users/product_detail.html', {'product': product})


def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_view")

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")

        # 1️⃣ Calculate total price first
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        if total_price <= 0:
            messages.error(request, "Your cart total is invalid.")
            return redirect("cart_view")

        # 2️⃣ Create order with correct total_price
        order = Order.objects.create(
            user=request.user,
            name=name,
            email=email,
            address=address,
            total_price=total_price,
            status="pending"
        )

        # 3️⃣ Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # 4️⃣ Redirect to Paystack
        return redirect("initialize-payment", order_id=order.id)

    return render(request, "users/checkout.html")

def initialize_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    print("===== PAYSTACK DEBUG START =====")
    print("ORDER ID:", order.id)
    print("ORDER TOTAL:", order.calculated_total_price)
    print("USER EMAIL:", request.user.email)

    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(order.total_price * 100),  # convert to kobo
        "reference": str(uuid.uuid4()),  # unique reference
        "callback_url": request.build_absolute_uri(f"/verify-payment/{order.id}/"),
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        print("STATUS CODE:", response.status_code)
        print("RAW RESPONSE:", response.text)

        response_data = response.json()
        print("JSON RESPONSE:", response_data)
        print("===== PAYSTACK DEBUG END =====")

        if response_data.get("status") is True:
            return redirect(response_data["data"]["authorization_url"])
        else:
            messages.error(request, response_data.get("message", "Payment initialization failed"))
            return redirect("payment-failed")

    except Exception as e:
        print("ERROR OCCURRED:", e)
        return redirect("payment-failed")
def verify_payment(request, order_id):
    reference = request.GET.get("reference")
    order = get_object_or_404(Order, id=order_id)

    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response_data.get("status") and response_data["data"]["status"] == "success":
        order.status = "paid"
        order.save()

 
        cart_items = CartItem.objects.filter(user=order.user)
        cart_items.delete()

        return redirect("order-success")
    else:
        order.status = "failed"
        order.save()
        return redirect("payment-failed")
def order_success(request):
    return render(request, "users/order_success.html")

def payment_failed(request):
    return render(request, "users/payment_failed.html")



@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    messages.success(request, "Item added to wishlist successfully!")

    return redirect('product_detail', id=product.id)
@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return redirect('wishlist')

@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, "users/wishlist.html", {"items": items})




@login_required
def toggle_wishlist(request, product_id):
    product = Products.objects.get(id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        wishlist_item.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "added"})



def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            user = User.objects.filter(email=email).first()

            if user:  # ✅ IMPORTANT CHECK
                token = PasswordResetToken.objects.create(user=user)

                reset_link = request.build_absolute_uri(
                    reverse("password-confirm", args=[token.token])
                )

                message = f"""
                Hello,

                Click the link below to reset your password:

               {reset_link}

              If you did not request this, ignore this email.
              """

                send_mail(
                    "Password Reset",
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

            # ✅ Always respond the same (security best practice)
            return redirect("password_reset_done")

    else:
        form = PasswordResetRequestForm()

    return render(request, "users/password_reset_request.html", {"form": form})

def reset_password(request, token):
    reset_token = get_object_or_404(PasswordResetToken, token=token)

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            user = reset_token.user
            user.password = make_password(password)
            user.save()
            reset_token.delete()
            return redirect("login")
    else:
        form = SetNewPasswordForm()
    
    return render(request, "users/password_reset_confirm.html", {"form": form})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/order_history.html', {'orders': orders})

@login_required
def transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/transactions.html', {'transactions': transactions})
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()

def create_superuser(request):
    if not User.objects.filter(email="admin@example.com").exists():
        User.objects.create_superuser(
            email="ariyoiseoluwa45@gmail.com",
            password="lighting",
        )
        return HttpResponse("Superuser created")
    return HttpResponse("Superuser already exists")
