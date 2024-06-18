from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from products.models import Order, Checkout, Product, UserCoupon
from products.views import total_cart_items
from users.models import Notification


# Create your views here.
@login_required
def update_notification(request):
    pass


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, transaction_id=order_id, user=request.user)
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([item.get_total for item in check_out_list])

    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    if get_cart_total >= 30000:
        get_shipping_fee = 0
    else:
        get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

    product_category = [item.product.category for item in order.order_item.all()]

    similar_items = Product.objects.filter(category__in=product_category).exclude(name__in=[item.product for item in order.order_item.all()]).order_by("?")[:2]

    used_coupon = UserCoupon.objects.filter(user=request.user).exists()
    coupon_value = UserCoupon.objects.all().first()
    context = {
        "check_out_list": check_out_list,
        "get_shipping_fee": get_shipping_fee,
        "get_cart_total": get_cart_total,
        "get_cart_items": total_cart_items(request),
        "notification": notification,
        "notification_count": notification_count,
        'order': order,
        'similar_items': similar_items,
        'used_coupon': used_coupon,
        'coupon_value': coupon_value,
    }
    return render(request, 'products/order_summary.html', context)


@login_required
def user_orders(request):
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([item.get_total for item in check_out_list])

    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    if get_cart_total >= 30000:
        get_shipping_fee = 0
    else:
        get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

    previous_orders = Order.objects.filter(user=request.user)
    context = {
        "check_out_list": check_out_list,
        "get_shipping_fee": get_shipping_fee,
        "get_cart_total": get_cart_total,
        "get_cart_items": total_cart_items(request),
        "notification": notification,
        "notification_count": notification_count,
        'orders': previous_orders,
        'items': previous_orders,

    }
    return render(request, 'users/previous_order.html', context)


def offline(request):
    return render(request, "users/offline.html")


def error_404(request, exception):
    data = {}
    return render(request, 'users/error404.html', data)


# def error_500(request):
#     data = {}
#     return render(request, 'users/error404.html', data)
#
#
# def error_400(request, exception):
#     data = {}
#     return render(request, 'users/error404.html', data)

