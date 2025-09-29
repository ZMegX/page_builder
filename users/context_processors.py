from django.conf import settings

def google_maps_key(request):
    return {"GOOGLE_MAPS_API_KEY": getattr(settings, "GOOGLE_MAPS_API_KEY", "")}

def cart_context(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return {
        'cart': cart,
        'total': total,
    }