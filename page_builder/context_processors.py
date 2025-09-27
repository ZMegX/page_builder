def is_customer(request):
    user = getattr(request, 'user', None)
    return user.is_authenticated and (
        hasattr(user, 'customer_profile') or user.groups.filter(name='Customer').exists()
    )

def customer_context(request):
    return {
        'is_customer': is_customer(request)
    }
from django.conf import settings

def google_maps_api_key(request):
    return {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}
