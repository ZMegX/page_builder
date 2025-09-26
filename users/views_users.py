from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import Order  # Adjust import if your Order model is elsewhere


@login_required
def order_detail(request, order_id):
	order = get_object_or_404(Order, id=order_id, customer=request.user)
	is_customer = request.user.is_authenticated and (
		hasattr(request.user, 'customer_profile') or request.user.groups.filter(name='Customer').exists()
	)
	return render(request, 'users/order_detail.html', {'order': order, 'is_customer': is_customer})


@login_required
def order_list(request):
	orders = Order.objects.filter(customer=request.user).order_by('-created_at')
	is_customer = request.user.is_authenticated and (
		hasattr(request.user, 'customer_profile') or request.user.groups.filter(name='Customer').exists()
	)
	return render(request, 'users/order_list.html', {'orders': orders, 'is_customer': is_customer})
