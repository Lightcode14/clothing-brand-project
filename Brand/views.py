from django.shortcuts import render

from users.models import Wishlist
from .models import Products
from django.contrib.auth.decorators import login_required
@login_required
def home(request):
    products=Products.objects.all().order_by('-created_at')

    wishlist_ids = []

    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    return render(request, "Brand/home.html", {
        "products": products,
        "wishlist_ids": wishlist_ids
    })



def landing(request):
    products = Products.objects.all()[:8]
    context = {
        "title": "TEMIHAVEN",
        "products": products
    }
    return render(request, 'Brand/landing.html', context)
@login_required
def new_arrivals(request):
    return render(request, "Brand/new_arrivals.html")
@login_required
def categories(request):
    return render(request, "Brand/categories.html")
@login_required
def customer_service(request):
    return render(request, "Brand/customer_service.html")

@login_required
def search_page(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Products.objects.filter(name__icontains=query)

    return render(request, 'Brand/search.html', {
        'query': query,
        'results': results
    })