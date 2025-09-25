from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import Order  # Adjust import if your Order model is elsewhere

@login_required
def order_detail(request, order_id):
	order = get_object_or_404(Order, id=order_id, customer=request.user)
	return render(request, 'users/order_detail.html', {'order': order})

@login_required
def order_list(request):
	orders = Order.objects.filter(customer=request.user).order_by('-created_at')
	return render(request, 'users/order_list.html', {'orders': orders})
