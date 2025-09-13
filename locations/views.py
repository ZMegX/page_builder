import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from locations.models import UserAddress
from users.models import RestaurantProfile 
from locations.serializers import AddressSerializer
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.conf import settings

@login_required
def map_view(request):
    """
    Renders the main map page.
    """

    context = {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }

    return render(request, 'locations/map.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def address_list_create(request):
    """
    GET: Returns a JSON list of all user addresses.
    POST: Creates a new user address from JSON data.
    """
    try:
            # Get the profile associated with the logged-in user.
        profile = RestaurantProfile.objects.get(user=request.user)
    except RestaurantProfile.DoesNotExist:
            # If no profile exists, return a clear error.
            return HttpResponseNotFound('RestaurantProfile not found for this user.')
    
    if request.method == 'GET':
        addresses = UserAddress.objects.filter(restaurant_profile=profile)
        serializer = AddressSerializer(addresses, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            if UserAddress.objects.filter(
                restaurant_profile=profile,
                formatted_address=data['formatted_address']).exists():
                return HttpResponseBadRequest('Address already exists.')
            
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
