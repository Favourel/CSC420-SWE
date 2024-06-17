import decimal
import json
from statistics import mean
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .filters import ProductPriceFilter
from .forms import ReviewBox, AddressForm, ApplyCouponForm
from .models import *
from users.models import *
from django.contrib import messages


# Create your views here.


def total_cart_items(request):
    check_out_list = Checkout.objects.filter(user=request.user, complete=False)
    get_cart_items = sum([item.quantity for item in check_out_list])
    return get_cart_items


def home(request):
    categories = Category.getAllCategory()[:7]
    products = Product.objects.all().order_by("?")[:8]

    if request.user.is_authenticated:
        notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
        notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
        get_cart_items = total_cart_items(request)
    else:
        notification = 0
        notification_count = 0
        get_cart_items = 0

    context = {
        "notification": notification,
        "notification_count": notification_count,
        "categories": categories,
        "products": products,
        "get_cart_items": get_cart_items,
    }
    return render(request, "products/home.html", context)


@login_required
def products_view(request):
    categories = Category.getAllCategory()
    products = Product.objects.all().order_by("date_posted")
    maximum_price = Product.objects.all().aggregate(Max("price"))
    half_max_price = maximum_price["price__max"] / 2

    price_filter = ProductPriceFilter(request.GET, queryset=products)
    products = price_filter.qs

    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    if request.GET.get('category_id'):
        filterProduct = Product.getProductByFilter(request.GET['category_id']).order_by('-id')
        filter_category_product = filterProduct.all().order_by('-product_purchase')

        price_filter = ProductPriceFilter(request.GET, queryset=filter_category_product)
        filter_category_product = price_filter.qs

        maximum_price = Product.objects.all().aggregate(Max("price"))
        half_max_price = maximum_price["price__max"] / 2

        notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
        notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

        check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
        get_cart_total = sum([item.get_total for item in check_out_list])
        if get_cart_total >= 200000:
            get_shipping_fee = 0
        else:
            get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

        paginator = Paginator(filter_category_product, 5)
        page_number = request.GET.get('page', 1)
        filter_category_product = paginator.get_page(page_number)

        return render(request, 'products/market.html', {
            # "price_filter": price_filter,
            "categories": categories,
            "notification": notification,
            "notification_count": notification_count,
            "products": filter_category_product,
            "maximum_price": maximum_price,
            "half_max_price": half_max_price,

            "get_cart_items": total_cart_items(request),
            "check_out_list": check_out_list,
            "get_shipping_fee": get_shipping_fee,
            "get_cart_total": get_cart_total,
        })
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([item.get_total for item in check_out_list])
    if get_cart_total >= 30000:
        get_shipping_fee = 0
    else:
        get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

    if request.GET.get('ratings'):
        query = request.GET.get('ratings')
        lookup = Q(rating_count=query)
        result = Product.objects.filter(lookup).distinct()
        price_filter = ProductPriceFilter(request.GET, queryset=result)
        result = price_filter.qs

        paginator = Paginator(result, 5)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
        get_cart_total = sum([item.get_total for item in check_out_list])
        if get_cart_total >= 30000:
            get_shipping_fee = 0
        else:
            get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

        context = {
            "products": products,

            "price_filter": price_filter,
            "categories": categories,
            "maximum_price": maximum_price,
            "half_max_price": half_max_price,

            "rating_query": query,
            "notification_count": notification_count,
            "notification": notification,
            "check_out_list": check_out_list,
            "get_shipping_fee": get_shipping_fee,
            "get_cart_items": total_cart_items(request)
        }

        return render(request, 'products/market.html', context)

    if request.GET.get('date_posted'):
        query = request.GET.get('date_posted')
        result = Product.objects.all().order_by(f"-{query}")
        price_filter = ProductPriceFilter(request.GET, queryset=result)
        product_list = price_filter.qs

        paginator = Paginator(result, 5)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
        get_cart_total = sum([item.get_total for item in check_out_list])
        if get_cart_total >= 30000:
            get_shipping_fee = 0
        else:
            get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

        context = {"products": products,

                   "categories": categories,
                   "maximum_price": maximum_price,
                   "half_max_price": half_max_price,
                   "product": product_list,
                   "rating_query": query,
                   "notification_count": notification_count,
                   "notification": notification,
                   "get_cart_items": total_cart_items(request),

                   "check_out_list": check_out_list,
                   "get_shipping_fee": get_shipping_fee,
                   }

        return render(request, 'products/market.html', context)

    context = {
        "notification": notification,
        "notification_count": notification_count,
        "categories": categories,
        "products": products,
        "get_cart_items": total_cart_items(request),

        "maximum_price": maximum_price,
        "half_max_price": half_max_price,

        "check_out_list": check_out_list,
        "get_shipping_fee": get_shipping_fee,
        "get_cart_total": get_cart_total,

    }
    return render(request, "products/market.html", context)


@login_required
def products_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    recently_viewed_products = []
    if 'recently_viewed_products' in request.session:
        recently_viewed_ids = request.session['recently_viewed_products']
        recently_viewed_products = Product.objects.filter(pk__in=recently_viewed_ids).exclude(pk=pk)

    ratings = [i.rating for i in product.productreview_set.all()]
    if len(ratings) < 1:
        overall_rating = 0
        one_star = 0
        two_star = 0
        three_star = 0
        four_star = 0
        five_star = 0
    else:
        overall_rating = mean(ratings)
        one_star = float(ratings.count(1) * 100) / len(ratings)
        two_star = float(ratings.count(2) * 100) / len(ratings)
        three_star = float(ratings.count(3) * 100) / len(ratings)
        four_star = float(ratings.count(4) * 100) / len(ratings)
        five_star = float(ratings.count(5) * 100) / len(ratings)

    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([item.get_total for item in check_out_list])
    if get_cart_total >= 30000:
        get_shipping_fee = 0
    else:
        get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

    context = {
        "check_out_list": check_out_list,
        "get_shipping_fee": get_shipping_fee,
        "get_cart_total": get_cart_total,
        "notification": notification,
        "notification_count": notification_count,
        "product": product,
        "recently_viewed_products": recently_viewed_products,
        "form": ReviewBox(),
        "get_cart_items": total_cart_items(request),

        "one_star": str(one_star)[:5],
        "two_star": str(two_star)[:5],
        "three_star": str(three_star)[:5],
        "four_star": str(four_star)[:5],
        "five_star": str(five_star)[:5],
        "overall_rating": str(overall_rating)[:3],
    }
    return render(request, "products/product_detail.html", context)


@login_required
def search_view(request):
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    if request.method == "GET":
        query = request.GET.get('q')
        submitbutton = request.GET.get('submit')
        if query is not None:
            lookups_product = Q(name__icontains=query)
            result_product = Product.objects.filter(lookups_product).distinct()
            check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
            get_cart_total = sum([item.get_total for item in check_out_list])
            if get_cart_total >= 30000:
                get_shipping_fee = 0
            else:
                get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])

            context = {
                "check_out_list": check_out_list,
                "get_shipping_fee": get_shipping_fee,
                "get_cart_total": get_cart_total,
                'submitbutton': submitbutton,

                "result_product": result_product,
                "notification_count": notification_count,
                "notification": notification,
                "get_cart_items": total_cart_items(request)
            }
            return render(request, "products/search.html", context)
        else:
            context = {
                'submitbutton': submitbutton,
                "notification_count": notification_count,
                "notification": notification,
                "get_cart_items": total_cart_items(request)
            }
            return render(request, 'products/search.html', context)
    return render(request, "products/search.html", {})


@login_required
def add_to_checkout(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    # checkout_list = Checkout.objects.filter(user=user, complete=False)

    create_object, created = Checkout.objects.get_or_create(
        user=user,
        product=product,
        complete=False,
    )
    create_object.quantity = (create_object.quantity + 1)
    create_object.price = (create_object.quantity * create_object.product.price)
    create_object.save()
    if create_object.quantity > 1:
        messages.success(request, f'"{product}" quantity has been updated!')
    else:
        messages.success(request, f'"{product}" has been added to your cart!')
    return redirect("checkout")


@login_required
def remove_from_checkout(request, pk):
    customer = request.user
    product = get_object_or_404(Product, pk=pk)
    orderItem, created = Checkout.objects.get_or_create(user=customer, product=product, complete=False)
    if Checkout.objects.filter(user=customer, product=product).exists():
        if orderItem.quantity <= 0:
            orderItem.delete()
            messages.success(request, f"'{product.name}' has been removed from your cart/checkout")
            return redirect("checkout")
        if orderItem.quantity >= 1:
            orderItem.quantity = (orderItem.quantity - 1)
            orderItem.price = (orderItem.quantity * orderItem.product.price)
            orderItem.save()
            messages.success(request, f"'{product.name}' quantity has been reduced from your cart/checkout")
            return redirect("checkout")
    else:
        messages.success(request, f"'{product.name}' has been removed from your cart/checkout")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    return render(request, 'market/checkout.html', {})


@login_required
def delete_from_checkout(request, pk):
    customer = request.user
    product = get_object_or_404(Product, pk=pk)
    print(Checkout.objects.filter(user=customer, product=product, complete=False))
    orderItem, created = Checkout.objects.get_or_create(user=customer, product=product, complete=False)
    if Checkout.objects.filter(user=customer, product=product, complete=False).exists():
        print(Checkout.objects.filter(user=customer, product=product, complete=False))
        orderItem.delete()
        messages.success(request, f"'{product.name}' has been removed from your cart")
        return redirect("checkout")
    else:
        messages.success(request, f"'{product.name}' doesn't exists in your cart")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def checkout(request):
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([item.get_total for item in check_out_list])
    if get_cart_total >= 30000:
        get_shipping_fee = 0
    else:
        get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])
    form = AddressForm()
    form_coupon = ApplyCouponForm()
    context = {
        "notification_count": notification_count,
        "notification": notification,
        "items": check_out_list,
        "form": form,
        "form_coupon": form_coupon,
        "check_out_list": check_out_list,

        "get_cart_total": get_cart_total,
        "get_shipping_fee": get_shipping_fee,
        "get_cart_items": total_cart_items(request),
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY
    }
    return render(request, "products/checkout.html", context)


@login_required
def process_order(request):
    data = json.loads(request.body)
    transaction_id = datetime.now().timestamp()
    reference = str(data['ref']['reference'])
    address = data.get('address')
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")

    queryset = []
    for item in check_out_list:
        queryset.append(item.complete == True)
        item.complete = True
        item.save()

    order = Order.objects.create(
        user=request.user,
        transaction_id=transaction_id,
        ordered=True,
        reference=reference,
        address=address,
        order_status="Pending",
    )

    order.order_item.set([item for item in check_out_list])
    order.default_order_item = [str(item) for item in order.order_item.all()]
    order.default_price = sum([item.get_total for item in check_out_list])
    order.save()

    product_queryset = []
    for item in check_out_list:
        product_queryset.append(item.product.product_purchase + item.quantity)
        item.product.product_purchase += item.quantity
        item.product.save()

    notification = Notification.objects.create(
        user=request.user,
        notification_type=1
    )
    notification.orders.set([item for item in check_out_list])
    notification.save()
    # return redirect('order_summary', order_id=order.id)

    return JsonResponse({'message': 'Payment complete!', 'redirect': f'{order.get_absolute_url()}'}, safe=False)


@login_required
def apply_coupon(request):
    if request.method == 'POST':
        form = ApplyCouponForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code=code)
                check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
                get_cart_total = sum([item.get_total for item in check_out_list])

                # Check if the user has made their first purchase
                if not Order.user_first_purchase(request.user):
                    messages.error(request, 'You need to make your first purchase before using a coupon')
                    return redirect("checkout")

                # Check if the user has already used this coupon
                user_coupon, created = UserCoupon.objects.get_or_create(user=request.user, coupon=coupon)
                if user_coupon.used:
                    messages.error(request, 'Coupon has already been used')
                    return redirect("checkout")

                # Mark the coupon as used
                user_coupon.used = True
                user_coupon.used_date = timezone.now()
                user_coupon.save()

                if coupon.is_valid(get_cart_total):  # Implement a method to check coupon validity

                    # Assuming you have retrieved a valid `coupon` object from the database

                    if coupon.discount_type == 'percentage':
                        discount_amount = int(decimal.Decimal(get_cart_total)) * (coupon.discount_value / 100)
                    elif coupon.discount_type == 'fixed_amount':
                        discount_amount = min(coupon.discount_value, get_cart_total)  # Limit discount to order total
                    else:
                        # Handle invalid discount type (optional)
                        raise ValueError("Invalid coupon discount type")

                    get_cart_total = decimal.Decimal(get_cart_total) - decimal.Decimal(discount_amount)

                    # Optionally, link the used coupon to the order
                    # order.coupon = coupon
                    # order.save()
                    print(get_cart_total, discount_amount)

                    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
                    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
                    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")

                    if get_cart_total >= 30000:
                        get_shipping_fee = 0
                    else:
                        get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])
                    form = AddressForm()
                    form_coupon = ApplyCouponForm()
                    # return HttpResponseRedirect(request.META.get("HTTP_REFERER"))  # Redirect to success page
                    context = {
                        "notification_count": notification_count,
                        "notification": notification,
                        "items": check_out_list,
                        "form": form,
                        "form_coupon": form_coupon,
                        "check_out_list": check_out_list,

                        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,

                        'get_cart_total': get_cart_total,
                        "get_cart_items": total_cart_items(request),
                        'discount': discount_amount,
                        'get_shipping_fee': get_shipping_fee
                    }
                    return render(request, 'products/checkout.html', context)

                else:
                    # Display error message - Coupon is not valid
                    messages.error(request, "Coupon code is not valid")
                    return redirect("checkout")
            except Coupon.DoesNotExist:
                # Display error message - Coupon code not found
                messages.error(request, "Coupon code not found or has expired")
                return redirect("checkout")
    else:

        return redirect("checkout")



@login_required
def product_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewBox(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.customer_info = request.user
            form.product = product
            form.default_product = str(product)
            form.save()

            ratings = [i.rating for i in product.productreview_set.all()]
            product.rating_count = round(mean(ratings))
            product.save()

    data = {
        "comment": request.POST.get('comment', None),
        "message": "Your review has been sent"
    }

    return JsonResponse(data)
