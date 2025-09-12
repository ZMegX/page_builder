import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import UserAddress
from django.shortcuts import render
from django.conf import settings
from users.models import RestaurantProfile 
from locations.serializers import AddressSerializer
from django.contrib.auth.decorators import login_required

@login_required
@require_http_methods(["GET", "POST"])
def address_list_create(request):
    """
    GET: Returns a JSON list of all user addresses.
    POST: Creates a new user address from JSON data.
    """
    profile = RestaurantProfile.objects.get(user=request.user)

    if request.method == 'GET':
        addresses = UserAddress.objects.filter(restaurant_profile=profile)
        serializer = AddressSerializer(addresses, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            address = UserAddress.objects.create(
                restaurant_profile=profile,
                formatted_address=data['formatted_address'],
                latitude=data['latitude'],
                longitude=data['longitude'],
            )
            serializer = AddressSerializer(address)
            return JsonResponse(serializer.data, status=201)
        except (KeyError, json.JSONDecodeError) as e:
            return HttpResponseBadRequest(f'Invalid data: {e}')
        
def map_view(request):
    """
    Renders the main map page.
    """
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    # You could pass the API key from settings.py if you want, but for now,
    # we'll keep it in the template for simplicity.
    return render(request, 'locations/map_view.html')