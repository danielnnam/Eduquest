# student/context_processors.py

from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.items.count() if cart else 0
    else:
        count = 0
    return {'cart_item_count': count}