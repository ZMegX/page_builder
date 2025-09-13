import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from locations.models import UserAddress
from users.models import RestaurantProfile 
from locations.serializers import AddressSerializer
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
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
            if 'formatted_address' not in data or 'latitude' not in data or 'longitude' not in data:
                 return JsonResponse({'error': 'Missing required address data.'}, status=400)
            
            if UserAddress.objects.filter(
                restaurant_profile=profile,
                formatted_address=data['formatted_address']).exists():
                return HttpResponse({'error': 'This address already exists.'}, status=409)
            
            address = UserAddress.objects.create(
                restaurant_profile=profile,
                formatted_address=data['formatted_address'],
                latitude=data['latitude'],
                longitude=data['longitude'],
            )
            serializer = AddressSerializer(address)
            return JsonResponse(serializer.data, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return HttpResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@login_required
@require_http_methods(["DELETE"])
def address_delete(request, pk):
    """
    Deletes an address. Ensures the address belongs to the logged-in user's profile.
    """
    print(f"--- address_delete view entered for pk={pk} ---")
    try:
        # Ensure the address exists and is owned by the user trying to delete it.
        address = UserAddress.objects.get(pk=pk, restaurant_profile__user=request.user)
        print(f"Found address: {address}")
        address.delete()
        print("Address deleted successfully.")
        return JsonResponse({'message': 'Address deleted successfully.'}, status=200)
    except UserAddress.DoesNotExist:
        print("Address.DoesNotExist exception caught.")
        return JsonResponse({'error': 'Address not found or you do not have permission to delete it.'}, status=404)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)